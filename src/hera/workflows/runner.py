"""The runner module contains the functionality required for the script runner."""
import argparse
import functools
import importlib
import inspect
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple, Union, cast

from pydantic import validate_arguments
from typing_extensions import get_args, get_origin

from hera.shared.serialization import serialize
from hera.workflows import Artifact, Parameter
from hera.workflows.artifact import ArtifactLoader
from hera.workflows.script import _extract_return_annotation_output

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore


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
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def _is_str_kwarg_of(key: str, f: Callable):
    """Check if param `key` of function `f` has a type annotation of a subclass of str."""
    type_ = inspect.signature(f).parameters[key].annotation
    if not type_:
        return True
    try:
        return issubclass(type_, str)
    except TypeError:
        # If this happens then it means that the annotation is a more complex type annotation
        # and may be interpretable by the Hera runner
        return False


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


def _map_keys(function: Callable, kwargs: dict) -> dict:
    """Change the kwargs's keys to use the Python name instead of the parameter name which could be kebab case.

    For Parameters, update their name to not contain kebab-case in Python but allow it in YAML.
    For Artifacts, load the Artifact according to the given ArtifactLoader.
    """
    if os.environ.get("hera__script_annotations", None) is None:
        return {key.replace("-", "_"): value for key, value in kwargs.items()}

    mapped_kwargs: Dict[str, Any] = {}
    for param_name, func_param in inspect.signature(function).parameters.items():
        if get_origin(func_param.annotation) is Annotated:
            annotated_type = get_args(func_param.annotation)[1]

            if isinstance(annotated_type, Parameter):
                if annotated_type.output:
                    if annotated_type.value_from and annotated_type.value_from.path:
                        mapped_kwargs[param_name] = Path(annotated_type.value_from.path)
                    else:
                        mapped_kwargs[param_name] = _get_outputs_path(annotated_type)
                    # Automatically create the parent directory (if required)
                    mapped_kwargs[param_name].parent.mkdir(parents=True, exist_ok=True)
                else:
                    mapped_kwargs[param_name] = kwargs[annotated_type.name]
            elif isinstance(annotated_type, Artifact):
                if annotated_type.output:
                    if annotated_type.path:
                        mapped_kwargs[param_name] = Path(annotated_type.path)
                    else:
                        mapped_kwargs[param_name] = _get_outputs_path(annotated_type)
                    # Automatically create the parent directory (if required)
                    mapped_kwargs[param_name].parent.mkdir(parents=True, exist_ok=True)
                elif annotated_type.path:
                    if annotated_type.loader == ArtifactLoader.json.value:
                        path = Path(annotated_type.path)
                        mapped_kwargs[param_name] = json.load(path.open())
                    elif annotated_type.loader == ArtifactLoader.file.value:
                        path = Path(annotated_type.path)
                        mapped_kwargs[param_name] = path.read_text()
                    elif annotated_type.loader is None:
                        mapped_kwargs[param_name] = annotated_type.path
        else:
            mapped_kwargs[param_name] = kwargs[param_name]

    return mapped_kwargs


def _save_annotated_return_outputs(
    function_outputs: Union[Tuple[Any], Any],
    output_destinations: List[Tuple[type, Union[Parameter, Artifact]]],
) -> None:
    """Save the outputs of the function to the specified output destinations.

    The output values are matched with the output annotations and saved using the schema:
    <parent_directory>/artifacts/<name>
    <parent_directory>/parameters/<name>
    If the artifact path or parameter value_from.path is specified, that is used instead.
    <parent_directory> can be provided by the user or is set to /tmp/hera/outputs by default
    """
    if not isinstance(function_outputs, tuple):
        function_outputs = [function_outputs]
    if len(function_outputs) != len(output_destinations):
        raise ValueError("The number of outputs does not match the annotation")

    for output_value, dest in zip(function_outputs, output_destinations):
        if not isinstance(output_value, dest[0]):
            raise ValueError(
                f"The type of output `{dest[1].name}`, `{type(output_value)}` does not match the annotated type `{dest[0]}`"
            )
        if not dest[1].name:
            raise ValueError("The name was not provided for one of the outputs.")

        path = _get_outputs_path(dest[1])
        _write_to_path(path, output_value)


def _get_outputs_path(destination: Union[Parameter, Artifact]) -> Path:
    """Get the path from the destination annotation using the defined outputs directory."""
    path = Path(os.environ.get("hera__outputs_directory", "/tmp/hera/outputs"))
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


def _runner(entrypoint: str, kwargs_list: Any) -> Any:
    """Run a function with a list of kwargs.

    Args:
        entrypoint: The path to the script within the container to execute.
        module: The module path to import the function from.
        function_name: The name of the function to run.
        kwargs_list: A list of kwargs to pass to the function.

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
    kwargs = _map_keys(function, kwargs)
    function = validate_arguments(function)
    function = _ignore_unmatched_kwargs(function)

    if os.environ.get("hera__script_annotations", None) is not None:
        output_annotations = _extract_return_annotation_output(function)

        if output_annotations:
            # This will save outputs returned from the function only. Any function parameters/artifacts marked as
            # outputs should be written to within the function itself.
            _save_annotated_return_outputs(function(**kwargs), output_annotations)
            return None

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
    result = _runner(args.entrypoint, kwargs_list)
    if not result:
        return
    print(serialize(result))


if __name__ == "__main__":
    _run()
