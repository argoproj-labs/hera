"""The runner module contains the functionality required for the script runner."""
import argparse
import functools
import importlib
import inspect
import json
import os
from pathlib import Path
from typing import Any, Callable, cast

from pydantic import validate_arguments
from typing_extensions import get_args, get_origin

from hera.shared.serialization import serialize
from hera.workflows import Artifact, Parameter
from hera.workflows.artifact import ArtifactLoader

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
    if _is_str_kwarg_of(key, f) or _is_artifact_loaded(key, f):
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
        # If this happens then it means that the annotation is complex type annotation
        # and may
        return False


def _is_artifact_loaded(key, f):
    """Check if param `key` of function `f` is actually an Artifact that has already been loaded."""
    param = inspect.signature(f).parameters[key]
    return (
        get_origin(param.annotation) is Annotated
        and isinstance(get_args(param.annotation)[1], Artifact)
        and get_args(param.annotation)[1].loader == ArtifactLoader.json.value
    )


def _map_keys(function: Callable, kwargs: dict) -> dict:
    """Change the kwargs's keys to use the python name instead of the parameter name which could be kebab case.

    For Parameters, update their name to not contain kebab-case in Python but allow it in YAML.
    For Artifacts, parse the contained info to get the path or object as needed.
    """
    if os.environ.get("hera__script_annotations", None) is None:
        return {key.replace("-", "_"): value for key, value in kwargs.items()}

    mapped_kwargs = {}
    for param_name, param in inspect.signature(function).parameters.items():
        if get_origin(param.annotation) is Annotated and isinstance(get_args(param.annotation)[1], Parameter):
            mapped_kwargs[param_name] = kwargs[get_args(param.annotation)[1].name]
        elif get_origin(param.annotation) is Annotated and isinstance(get_args(param.annotation)[1], Artifact):
            if get_args(param.annotation)[1].loader == ArtifactLoader.json.value:
                path = Path(get_args(param.annotation)[1].path)
                mapped_kwargs[param_name] = json.load(path.open())
            elif get_args(param.annotation)[1].loader == ArtifactLoader.file.value:
                path = Path(get_args(param.annotation)[1].path)
                mapped_kwargs[param_name] = path.read_text()
            elif get_args(param.annotation)[1].loader is None:
                mapped_kwargs[param_name] = get_args(param.annotation)[1].path
        else:
            mapped_kwargs[param_name] = kwargs[param_name]
    return mapped_kwargs


def _runner(entrypoint: str, kwargs_list: Any) -> str:
    """Run a function with a list of kwargs.

    Args:
        entrypoint: The path to the script within the container to execute.
        module: The module path to import the function from.
        function_name: The name of the function to run.
        kwargs_list: A list of kwargs to pass to the function.

    Returns:
        The result of the function as a string.
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
    kwargs_list = json.loads(args.args_path.read_text() or r"[]")
    result = _runner(args.entrypoint, kwargs_list)
    if not result:
        return
    print(serialize(result))


if __name__ == "__main__":
    _run()
