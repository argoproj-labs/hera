"""The runner module contains the functionality required for the script runner."""
import argparse
import functools
import importlib
import inspect
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union, cast

from hera.shared._pydantic import _PYDANTIC_VERSION
from hera.shared.serialization import serialize
from hera.workflows import Artifact, Parameter
from hera.workflows.artifact import ArtifactLoader
from hera.workflows.io.v1 import (
    RunnerInput as RunnerInputV1,
    RunnerOutput as RunnerOutputV1,
)

try:
    from hera.workflows.io.v2 import (  # type: ignore
        RunnerInput as RunnerInputV2,
        RunnerOutput as RunnerOutputV2,
    )
except ImportError:
    from hera.workflows.io.v1 import (  # type: ignore
        RunnerInput as RunnerInputV2,
        RunnerOutput as RunnerOutputV2,
    )
from hera.workflows.script import _extract_return_annotation_output

try:
    from typing import Annotated, get_args, get_origin  # type: ignore
except ImportError:
    from typing_extensions import Annotated, get_args, get_origin  # type: ignore

try:
    from pydantic.type_adapter import TypeAdapter  # type: ignore
    from pydantic.v1 import parse_obj_as  # type: ignore
except ImportError:
    from pydantic import parse_obj_as


def _ignore_unmatched_kwargs(f):
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


def _parse(value, key, f):
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
        if os.environ.get("hera__script_annotations", None) is None:
            return json.loads(value)

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


def _get_type(key: str, f: Callable) -> Optional[type]:
    type_ = inspect.signature(f).parameters[key].annotation
    if type_ is inspect.Parameter.empty:
        return None
    if get_origin(type_) is None:
        return type_
    origin_type = cast(type, get_origin(type_))
    if origin_type is Annotated:
        return get_args(type_)[0]
    return origin_type


def _get_unannotated_type(key: str, f: Callable) -> Optional[type]:
    """Get the type of function param without the 'Annotated' outer type."""
    type_ = inspect.signature(f).parameters[key].annotation
    if type_ is inspect.Parameter.empty:
        return None
    if get_origin(type_) is None:
        return type_

    origin_type = cast(type, get_origin(type_))
    if origin_type is Annotated:
        return get_args(type_)[0]

    # Type could be a dict/list with subscript type
    return type_


def _is_str_kwarg_of(key: str, f: Callable) -> bool:
    """Check if param `key` of function `f` has a type annotation of a subclass of str."""
    type_ = _get_type(key, f)
    if type_ is None:
        return False
    return issubclass(type_, str)


def _is_artifact_loaded(key, f):
    """Check if param `key` of function `f` is actually an Artifact that has already been loaded."""
    param = inspect.signature(f).parameters[key]
    return (
        get_origin(param.annotation) is Annotated
        and isinstance(get_args(param.annotation)[1], Artifact)
        and get_args(param.annotation)[1].loader == ArtifactLoader.json.value
    )


def _is_output_kwarg(key, f):
    """Check if param `key` of function `f` is an output Artifact/Parameter."""
    param = inspect.signature(f).parameters[key]
    return (
        get_origin(param.annotation) is Annotated
        and isinstance(get_args(param.annotation)[1], (Artifact, Parameter))
        and get_args(param.annotation)[1].output
    )


def _map_argo_inputs_to_function(function: Callable, kwargs: Dict) -> Dict:
    """Map kwargs from Argo to the function parameters using the function's parameter annotations.

    For Parameter inputs:
    * if the Parameter has a "name", replace it with the function parameter name
    * otherwise use the function parameter name as-is
    For Parameter outputs:
    * update value to a Path object from the value_from.path value, or the default if not provided

    For Artifact inputs:
    * load the Artifact according to the given ArtifactLoader
    For Artifact outputs:
    * update value to a Path object
    """
    mapped_kwargs: Dict[str, Any] = {}

    def map_annotated_param(param_name: str, param_annotation: Parameter) -> None:
        if param_annotation.output:
            if param_annotation.value_from and param_annotation.value_from.path:
                mapped_kwargs[param_name] = Path(param_annotation.value_from.path)
            else:
                mapped_kwargs[param_name] = _get_outputs_path(param_annotation)
            # Automatically create the parent directory (if required)
            mapped_kwargs[param_name].parent.mkdir(parents=True, exist_ok=True)
        elif param_annotation.name:
            mapped_kwargs[param_name] = kwargs[param_annotation.name]
        else:
            mapped_kwargs[param_name] = kwargs[param_name]

    def map_annotated_artifact(param_name: str, artifact_annotation: Artifact) -> None:
        if artifact_annotation.output:
            if artifact_annotation.path:
                mapped_kwargs[param_name] = Path(artifact_annotation.path)
            else:
                mapped_kwargs[param_name] = _get_outputs_path(artifact_annotation)
            # Automatically create the parent directory (if required)
            mapped_kwargs[param_name].parent.mkdir(parents=True, exist_ok=True)
        else:
            if not artifact_annotation.path:
                # Path was added to yaml automatically, we need to add it back in for the runner
                artifact_annotation.path = artifact_annotation._get_default_inputs_path()

            if artifact_annotation.loader == ArtifactLoader.json.value:
                path = Path(artifact_annotation.path)
                mapped_kwargs[param_name] = json.load(path.open())
            elif artifact_annotation.loader == ArtifactLoader.file.value:
                path = Path(artifact_annotation.path)
                mapped_kwargs[param_name] = path.read_text()
            elif artifact_annotation.loader is None:
                mapped_kwargs[param_name] = artifact_annotation.path

    T = TypeVar("T", bound=Union[RunnerInputV1, RunnerInputV2])

    def map_runner_input(param_name: str, runner_input_class: T):
        """Map argo input kwargs to the fields of the given RunnerInput.

        If the field is annotated, we look for the kwarg with the name from the annotation (Parameter or Artifact).
        Otherwise, we look for the kwarg with the name of the field.
        """
        input_model_obj = {}

        def map_field(field: str) -> Optional[str]:
            annotation = runner_input_class.__annotations__[field]
            if get_origin(annotation) is Annotated:
                annotation = get_args(annotation)[1]
                if isinstance(annotation, Parameter):
                    map_annotated_param(field, annotation)
                    mapped_kwargs[field] = json.loads(mapped_kwargs[field])
                elif isinstance(annotation, Artifact):
                    map_annotated_artifact(field, annotation)
            else:
                mapped_kwargs[field] = json.loads(kwargs[field])

            return field

        for field in runner_input_class.__fields__:
            matched_field = map_field(field)
            if matched_field:
                input_model_obj[field] = mapped_kwargs[matched_field]

        mapped_kwargs[param_name] = runner_input_class.parse_raw(json.dumps(input_model_obj))

    for param_name, func_param in inspect.signature(function).parameters.items():
        if get_origin(func_param.annotation) is Annotated:
            func_param_annotation = get_args(func_param.annotation)[1]

            if isinstance(func_param_annotation, Parameter):
                map_annotated_param(param_name, func_param_annotation)
            elif isinstance(func_param_annotation, Artifact):
                map_annotated_artifact(param_name, func_param_annotation)
            else:
                mapped_kwargs[param_name] = kwargs[param_name]
        elif get_origin(func_param.annotation) is None and issubclass(
            func_param.annotation, (RunnerInputV1, RunnerInputV2)
        ):
            map_runner_input(param_name, func_param.annotation)
        else:
            mapped_kwargs[param_name] = kwargs[param_name]
    return mapped_kwargs


def _save_annotated_return_outputs(
    function_outputs: Union[Tuple[Any], Any],
    output_annotations: List[
        Union[Tuple[type, Union[Parameter, Artifact]], Union[Type[RunnerOutputV1], Type[RunnerOutputV2]]]
    ],
) -> Optional[Union[RunnerOutputV1, RunnerOutputV2]]:
    """Save the outputs of the function to the specified output destinations.

    The output values are matched with the output annotations and saved using the schema:
    <parent_directory>/artifacts/<name>
    <parent_directory>/parameters/<name>
    If the artifact path or parameter value_from.path is specified, that is used instead.
    <parent_directory> can be provided by the user or is set to /tmp/hera-outputs by default
    """
    if not isinstance(function_outputs, tuple):
        function_outputs = [function_outputs]
    if len(function_outputs) != len(output_annotations):
        raise ValueError("The number of outputs does not match the annotation")

    if os.environ.get("hera__script_pydantic_io", None) is not None:
        return_obj = None

    for output_value, dest in zip(function_outputs, output_annotations):
        if isinstance(output_value, (RunnerOutputV1, RunnerOutputV2)):
            if os.environ.get("hera__script_pydantic_io", None) is None:
                raise ValueError("hera__script_pydantic_io environment variable is not set")

            return_obj = output_value

            for field, value in output_value.dict().items():
                if field in {"exit_code", "result"}:
                    continue

                matching_output = output_value._get_output(field)
                path = _get_outputs_path(matching_output)
                _write_to_path(path, value)
        else:
            assert isinstance(dest, tuple)
            if get_origin(dest[0]) is None:
                # Built-in types return None from get_origin, so we can check isinstance directly
                if not isinstance(output_value, dest[0]):
                    raise ValueError(
                        f"The type of output `{dest[1].name}`, `{type(output_value)}` does not match the annotated type `{dest[0]}`"
                    )
            else:
                # Here, we know get_origin is not None, but its return type is found to be `Optional[Any]`
                origin_type = cast(type, get_origin(dest[0]))
                if not isinstance(output_value, origin_type):
                    raise ValueError(
                        f"The type of output `{dest[1].name}`, `{type(output_value)}` does not match the annotated type `{dest[0]}`"
                    )

            if not dest[1].name:
                raise ValueError("The name was not provided for one of the outputs.")

            path = _get_outputs_path(dest[1])
            _write_to_path(path, output_value)

    if os.environ.get("hera__script_pydantic_io", None) is not None:
        return return_obj

    return None


def _save_dummy_outputs(
    output_annotations: List[
        Union[Tuple[type, Union[Parameter, Artifact]], Union[Type[RunnerOutputV1], Type[RunnerOutputV2]]]
    ],
) -> None:
    """Save dummy values into the outputs specified.

    This function is used at runtime by the Hera Runner to create files in the container so that Argo
    does not log confusing error messages that obfuscate the real error, which look like:
    ```
    msg="cannot save parameter /tmp/hera-outputs/parameters/my-parameter"
    argo=true
    error="open /tmp/hera-outputs/parameters/my-parameter: no such file or directory"`
    ```

    The output annotations are used to write files using the schema:
    <parent_directory>/artifacts/<name>
    <parent_directory>/parameters/<name>
    If the artifact path or parameter value_from.path is specified, that is used instead.
    <parent_directory> can be provided by the user or is set to /tmp/hera-outputs by default
    """
    for dest in output_annotations:
        if isinstance(dest, (RunnerOutputV1, RunnerOutputV2)):
            if os.environ.get("hera__script_pydantic_io", None) is None:
                raise ValueError("hera__script_pydantic_io environment variable is not set")

            for field, _ in dest.__fields__:
                if field in {"exit_code", "result"}:
                    continue

                annotation = dest._get_output(field)
                path = _get_outputs_path(annotation)
                _write_to_path(path, "")
        else:
            if not dest[1].name:
                raise ValueError("The name was not provided for one of the outputs.")

            path = _get_outputs_path(dest[1])
            _write_to_path(path, "")


def _get_outputs_path(destination: Union[Parameter, Artifact]) -> Path:
    """Get the path from the destination annotation using the defined outputs directory."""
    path = Path(os.environ.get("hera__outputs_directory", "/tmp/hera-outputs"))
    if isinstance(destination, Parameter) and destination.name:
        path = path / f"parameters/{destination.name}"
    elif isinstance(destination, Artifact):
        if destination.path:
            path = Path(destination.path)
        elif destination.name:
            path = path / f"artifacts/{destination.name}"
    return path


def _write_to_path(path: Path, output_value: Any) -> None:
    """Write the output_value as serialized text to the provided path. Create the necessary parent directories."""
    output_string = serialize(output_value)
    if output_string is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output_string)


def _runner(entrypoint: str, kwargs_list: List) -> Any:
    """Run the function defined by the entrypoint with the given list of kwargs.

    Args:
        entrypoint: The module path to the script within the container to execute. "package.submodule:function"
        kwargs_list: A list of dicts with "name" and "value" keys, representing the kwargs of the function.

    Returns:
        The result of the function or `None` if the outputs are to be saved.
    """
    # import the module and get the function
    module, function_name = entrypoint.split(":")
    function = getattr(importlib.import_module(module), function_name)
    # if the function is wrapped, unwrap it
    # this may happen if the function is decorated with @script
    if hasattr(function, "wrapped_function"):
        function = function.wrapped_function
    # convert the kwargs list to a dict
    kwargs = {}
    for kwarg in kwargs_list:
        if "name" not in kwarg or "value" not in kwarg:
            continue
        # sanitize the key for python
        key = cast(str, serialize(kwarg["name"]))
        value = kwarg["value"]
        kwargs[key] = value

    if os.environ.get("hera__script_annotations", None) is None:
        # Do a simple replacement for hyphens to get valid Python parameter names.
        kwargs = {key.replace("-", "_"): value for key, value in kwargs.items()}
    else:
        kwargs = _map_argo_inputs_to_function(function, kwargs)

    # The imported validate_arguments uses smart union by default just in case clients do not rely on it. This means that if a function uses a union
    # type for any of its inputs, then this will at least try to map those types correctly if the input object is
    # not a pydantic model with smart_union enabled
    _pydantic_mode = int(os.environ.get("hera__pydantic_mode", _PYDANTIC_VERSION))
    if _pydantic_mode == 2:
        from pydantic import validate_call  # type: ignore

        function = validate_call(function)
    else:
        if _PYDANTIC_VERSION == 1:
            from pydantic import validate_arguments
        else:
            from pydantic.v1 import validate_arguments  # type: ignore
        function = validate_arguments(function, config=dict(smart_union=True, arbitrary_types_allowed=True))  # type: ignore

    function = _ignore_unmatched_kwargs(function)

    if os.environ.get("hera__script_annotations", None) is not None:
        output_annotations = _extract_return_annotation_output(function)

        if output_annotations:
            # This will save outputs returned from the function only. Any function parameters/artifacts marked as
            # outputs should be written to within the function itself.
            try:
                output = _save_annotated_return_outputs(function(**kwargs), output_annotations)
            except Exception as e:
                _save_dummy_outputs(output_annotations)
                raise e
            return output or None

    return function(**kwargs)


def _parse_args():
    """Creates an argparse for the runner function.

    The returned argparse takes a module and function name as flags and a path to a json file as an argument.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--entrypoint", "-e", type=str, required=True)
    parser.add_argument("args_path", type=Path)
    return parser.parse_args()


def _run():
    """Runs a function from a specific path using parsed arguments from Argo.

    Note that this prints the result of the function to stdout, which is the normal mode of operation for Argo. Any
    output of a Python function submitted via a `Script.source` field results in outputs sent to stdout.
    """
    args = _parse_args()
    # 1. Protect against trying to json.loads on empty files with inner `or r"[]`
    # 2. Protect against files containing `null` as text with outer `or []` (as a result of using
    #    `{{inputs.parameters}}` where the parameters key doesn't exist in `inputs`)
    kwargs_list = json.loads(args.args_path.read_text() or r"[]") or []
    assert isinstance(kwargs_list, List)
    result = _runner(args.entrypoint, kwargs_list)
    if not result:
        return

    if isinstance(result, (RunnerOutputV1, RunnerOutputV2)):
        print(serialize(result.result))
        exit(result.exit_code)

    print(serialize(result))


if __name__ == "__main__":
    _run()
