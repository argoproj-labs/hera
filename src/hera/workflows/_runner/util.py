"""The util module contains the functionality required for the script runner."""

import argparse
import functools
import importlib
import inspect
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, cast

if sys.version_info >= (3, 10):
    from types import NoneType
else:
    NoneType = type(None)

from hera.shared._pydantic import _PYDANTIC_VERSION
from hera.shared._type_util import (
    get_workflow_annotation,
    is_annotated,
    is_subscripted,
    origin_type_issubtype,
    unwrap_annotation,
)
from hera.shared.serialization import serialize
from hera.workflows import Artifact, Parameter
from hera.workflows._runner.script_annotations_util import (
    _save_annotated_return_outputs,
    _save_dummy_outputs,
    get_annotated_artifact_value,
    get_annotated_input_param,
    get_annotated_output_param,
    load_param_input,
    map_runner_input,
)
from hera.workflows.artifact import ArtifactLoader
from hera.workflows.io.v1 import (
    Input as InputV1,
    Output as OutputV1,
)
from hera.workflows.script import _extract_return_annotation_output

if _PYDANTIC_VERSION == 2:
    from pydantic.type_adapter import TypeAdapter  # type: ignore
    from pydantic.v1 import parse_obj_as  # type: ignore

    from hera.workflows.io.v2 import (  # type: ignore
        Input as InputV2,
        Output as OutputV2,
    )
else:
    from pydantic import parse_obj_as

    from hera.workflows.io.v1 import (  # type: ignore
        Input as InputV2,
        Output as OutputV2,
    )


def _ignore_unmatched_kwargs(f: Callable) -> Callable:
    """Make function ignore unmatched kwargs.

    If the function already has the catch all **kwargs, do nothing.
    """
    if _contains_var_kwarg(f):
        return f

    @functools.wraps(f)
    def inner(**kwargs):
        # filter out kwargs that are not part of the function signature
        # and transform them to the correct type
        filtered_kwargs = {key: _parse(value, key, f) for key, value in kwargs.items() if _is_kwarg_of(key, f)}
        return f(**filtered_kwargs)

    return inner


def _contains_var_kwarg(f: Callable) -> bool:
    """Tells whether the given callable contains a keyword argument."""
    return any(param.kind == inspect.Parameter.VAR_KEYWORD for param in inspect.signature(f).parameters.values())


def _is_kwarg_of(key: str, f: Callable) -> bool:
    """Tells whether the given `key` identifies a keyword argument of the given callable."""
    param = inspect.signature(f).parameters.get(key)
    return param is not None and (
        param.kind is inspect.Parameter.KEYWORD_ONLY or param.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    )


def _parse(value: str, key: str, f: Callable) -> Any:
    """Parse a value to the correct type.

    Args:
        value: The value to parse.
        key: The name of the kwarg.
        f: The function to parse the value for.

    Returns:
        The parsed value.

    """
    if _is_str_kwarg_of(key, f) or _is_artifact_loaded(key, f) or _is_output_kwarg(key, f):
        return value
    try:
        type_ = _get_unannotated_type(key, f)
        loaded_json_value = json.loads(value)

        if not type_:
            return loaded_json_value

        _pydantic_mode = int(os.environ.get("hera__pydantic_mode", _PYDANTIC_VERSION))
        if _pydantic_mode == 1:
            return parse_obj_as(type_, loaded_json_value)
        else:
            return TypeAdapter(type_).validate_python(loaded_json_value)
    except (json.JSONDecodeError, TypeError):
        return value


def _get_function_param_annotation(key: str, f: Callable) -> Optional[type]:
    func_param_annotation = inspect.signature(f).parameters[key].annotation
    if func_param_annotation is inspect.Parameter.empty:
        return None
    return func_param_annotation


def _get_unannotated_type(key: str, f: Callable) -> Optional[type]:
    """Get the type of function param without the 'Annotated' outer type."""
    type_ = _get_function_param_annotation(key, f)
    if type_ is None:
        return None
    return unwrap_annotation(type_)


def _is_str_kwarg_of(key: str, f: Callable) -> bool:
    """Check if param `key` of function `f` has a type annotation that can be interpreted as a subclass of str."""
    if func_param_annotation := _get_function_param_annotation(key, f):
        return origin_type_issubtype(func_param_annotation, (str, NoneType))
    return False


def _is_artifact_loaded(key: str, f: Callable) -> bool:
    """Check if param `key` of function `f` is actually an Artifact that has already been loaded."""
    if param_annotation := _get_function_param_annotation(key, f):
        if (artifact := get_workflow_annotation(param_annotation)) and isinstance(artifact, Artifact):
            return (
                artifact.loader == ArtifactLoader.json.value
                or artifact.loads is not None
                or artifact.loadb is not None
            )
    return False


def _is_output_kwarg(key: str, f: Callable) -> bool:
    """Check if param `key` of function `f` is an output Artifact/Parameter."""
    if param_annotation := _get_function_param_annotation(key, f):
        if param_or_artifact := get_workflow_annotation(param_annotation):
            return bool(param_or_artifact.output)
    return False


def _map_function_annotations(function: Callable, template_inputs: Dict[str, str]) -> Dict:
    """Parse annotations to substitute values from Argo for the function parameters.

    For Parameter inputs:
    * if the Parameter has a "name", replace it with the function parameter name
    * otherwise use the function parameter name as-is
    * use the Parameter loader if provided
    For Parameter outputs:
    * update value to a Path object from the value_from.path value, or the default if not provided

    For Artifact inputs:
    * load the Artifact according to the given ArtifactLoader
    For Artifact outputs:
    * update value to a Path object
    """
    if _contains_var_kwarg(function):
        return template_inputs

    function_kwargs: Dict[str, Any] = {}

    # Iterate over the _function parameters_ and map the template inputs to them
    # e.g. for `function=func(param: Annotated[int, Parameter(name="my-param")])`,
    # and template_inputs={"my-param": "5"}, the function_kwargs will be {"param": 5}
    for func_param_name, func_param in inspect.signature(function).parameters.items():
        if param_or_artifact := get_workflow_annotation(func_param.annotation):
            if isinstance(param_or_artifact, Parameter):
                if param_or_artifact.output:
                    function_kwargs[func_param_name] = get_annotated_output_param(param_or_artifact)
                else:
                    param_value = get_annotated_input_param(func_param_name, param_or_artifact, template_inputs)

                    function_kwargs[func_param_name] = load_param_input(param_value, param_or_artifact.loads)
            else:
                function_kwargs[func_param_name] = get_annotated_artifact_value(func_param_name, param_or_artifact)

        elif not is_subscripted(func_param.annotation) and issubclass(func_param.annotation, (InputV1, InputV2)):
            # We collect all relevant kwargs for the single `Input` function parameter
            function_kwargs[func_param_name] = map_runner_input(func_param.annotation, template_inputs)
        elif (
            is_annotated(func_param.annotation)
            and inspect.isclass(unwrap_annotation(func_param.annotation))
            and issubclass(unwrap_annotation(func_param.annotation), (InputV1, InputV2))
        ):
            function_kwargs[func_param_name] = map_runner_input(
                unwrap_annotation(func_param.annotation), template_inputs
            )
        else:
            # Use the kwarg value as-is
            function_kwargs[func_param_name] = template_inputs[func_param_name]
    return function_kwargs


def _runner(entrypoint: str, template_inputs_list: List) -> Any:
    """Run the function defined by the entrypoint with the given list of kwargs.

    Args:
        entrypoint: The module path to the script within the container to execute. "package.submodule:function"
        template_inputs_list: A list of dicts with "name" and "value" keys, to be mapped to the kwargs of the function.

    Returns:
        The result of the function or `None` if the outputs are to be saved.
    """
    # import the module and get the function
    module, function_name = entrypoint.split(":")
    function: Callable = getattr(importlib.import_module(module), function_name)
    # if the function is wrapped, unwrap it
    # this may happen if the function is decorated with @script
    if hasattr(function, "wrapped_function"):
        function = function.wrapped_function

    # convert the template inputs list to a dict
    template_inputs: Dict[str, str] = {}
    for kwarg in template_inputs_list:
        if "name" not in kwarg or "value" not in kwarg:
            continue
        # sanitize the key for python
        key = cast(str, serialize(kwarg["name"]))
        value = kwarg["value"]
        template_inputs[key] = value

    function_kwargs = _map_function_annotations(function, template_inputs)

    # The imported validate_arguments uses smart union by default just in case clients do not rely on it. This means that if a function uses a union
    # type for any of its inputs, then this will at least try to map those types correctly if the input object is
    # not a pydantic model with smart_union enabled
    _pydantic_mode = int(os.environ.get("hera__pydantic_mode", _PYDANTIC_VERSION))
    if _pydantic_mode == 2:
        from pydantic import ConfigDict, validate_call  # type: ignore

        function = validate_call(config=ConfigDict(arbitrary_types_allowed=True))(function)
    else:
        from pydantic.v1 import validate_arguments

        function = validate_arguments(config=dict(smart_union=True, arbitrary_types_allowed=True))(function)

    function = _ignore_unmatched_kwargs(function)

    output_annotations = _extract_return_annotation_output(function)

    if output_annotations:
        # This will save outputs returned from the function only. Any function parameters/artifacts marked as
        # outputs should be written to within the function itself.
        try:
            output = _save_annotated_return_outputs(function(**function_kwargs), output_annotations)
        except Exception as e:
            _save_dummy_outputs(output_annotations)
            raise e
        return output or None

    return function(**function_kwargs)


def _parse_args() -> argparse.Namespace:
    """Creates an argparse for the runner function.

    The returned argparse takes a module and function name as flags and a path to a json file as an argument.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--entrypoint", "-e", type=str, required=True)
    parser.add_argument("args_path", type=Path)
    return parser.parse_args()


def _run() -> None:
    """Runs a function from a specific path using parsed arguments from Argo.

    Note that this prints the result of the function to stdout, which is the normal mode of operation for Argo. Any
    output of a Python function submitted via a `Script.source` field results in outputs sent to stdout.
    """
    args = _parse_args()
    # 1. Protect against trying to json.loads on empty files with inner `or r"[]`
    # 2. Protect against files containing `null` as text with outer `or []` (as a result of using
    #    `{{inputs.parameters}}` where the parameters key doesn't exist in `inputs`)
    template_inputs = json.loads(args.args_path.read_text() or r"[]") or []
    assert isinstance(template_inputs, List)
    result = _runner(args.entrypoint, template_inputs)
    if not result:
        return

    if isinstance(result, (OutputV1, OutputV2)):
        print(serialize(result.result))
        exit(result.exit_code)

    print(serialize(result))


def create_module_string(path: Path) -> str:
    """Create a Python module path from the given path.

    We find the most specific sys.path to create a valid, importable module path to the given path.

    e.g. if sys.path contains "/project" and the file is "/project/workflows/wf_a.py", then the returned string will be
    "workflows.wf_a"

    If we cannot find a valid sys.path, we simply use the file stem, e.g. for the
    file "/project/workflows/wf_a.py", return `wf_a`.
    """
    path = path.resolve()

    # find the most specific sys.path that contains the given path
    candidates = []
    for base in map(lambda p: Path(p).resolve(), sys.path + [os.getcwd()]):
        if path.is_relative_to(base):
            candidates.append(base)

    if not candidates:
        return path.stem

    # use the most specific sys.path to construct a valid module path to import
    base_path = max(candidates, key=lambda p: len(str(p)))
    return ".".join(str(path.resolve().relative_to(base_path)).replace(".py", "").split("/"))
