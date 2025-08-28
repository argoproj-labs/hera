"""The script_annotations_util module contains functionality for the script annotations feature when used with the runner."""

import json
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union, cast

if sys.version_info >= (3, 10):
    from types import NoneType
else:
    NoneType = type(None)

from hera.shared._pydantic import BaseModel, get_field_annotations, get_fields
from hera.shared._type_util import (
    get_unsubscripted_type,
    get_workflow_annotation,
    origin_type_issubtype,
    unwrap_annotation,
)
from hera.shared.serialization import serialize
from hera.workflows import Artifact, Parameter
from hera.workflows.artifact import ArtifactLoader
from hera.workflows.io.v1 import Output as OutputV1

try:
    from hera.workflows.io.v2 import Output as OutputV2
except ImportError:
    from hera.workflows.io.v1 import Output as OutputV2  # type: ignore


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


def _get_dumper_function(destination: Union[Parameter, Artifact]) -> Callable:
    if destination.dumps is not None:
        return destination.dumps
    if isinstance(destination, Artifact) and destination.dumpb is not None:
        return destination.dumpb

    return serialize


def get_annotated_input_param(
    func_param_name: str,
    param_annotation: Parameter,
    kwargs: Dict[str, str],
) -> str:
    """Get the value from a given function param and its annotation.

    Return the string value from the kwargs dict,
    which could be from the param_annotation.name if given, or func_param_name.
    """
    if param_annotation.name in kwargs:
        return kwargs[param_annotation.name]

    if func_param_name in kwargs:
        return kwargs[func_param_name]

    raise RuntimeError(
        f"Parameter {param_annotation.name if param_annotation.name else func_param_name} was not given a value"
    )


def load_param_input(
    param_value: str,
    loader: Optional[Callable[[str], Any]],
) -> Any:
    return param_value if loader is None else loader(param_value)


def get_annotated_output_param(param_annotation: Parameter) -> Path:
    if param_annotation.value_from and param_annotation.value_from.path:
        path = Path(param_annotation.value_from.path)
    else:
        path = _get_outputs_path(param_annotation)
    # Automatically create the parent directory (if required)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_annotated_output_artifact(artifact_annotation: Artifact) -> Path:
    if artifact_annotation.path:
        path = Path(artifact_annotation.path)
    else:
        path = _get_outputs_path(artifact_annotation)
    # Automatically create the parent directory (if required)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_annotated_artifact_value(param_name: str, artifact_annotation: Artifact) -> Union[Path, Any]:
    """Get the value of the given Artifact annotation.

    If the artifact is an output, return the path it will write to.
    If the artifact is an input, and one of the `loads` or `load` functions are not None,
    they are used directly to load the value.
    Otherwise, if it has an ArtifactLoader enum as its loader, return the
    loaded value according to the predefined behaviour (json obj, path or string).
    """
    if artifact_annotation.output:
        return get_annotated_output_artifact(artifact_annotation)

    if not artifact_annotation.name:
        artifact_annotation.name = param_name

    if not artifact_annotation.path:
        # Path is added to the spec automatically when built. As it isn't present in the annotation itself,
        # we need to add it back in for the runner.
        artifact_annotation.path = artifact_annotation._get_default_inputs_path()

    path = Path(artifact_annotation.path)
    if artifact_annotation.optional and not path.exists():
        return None

    if artifact_annotation.loads is not None:
        return artifact_annotation.loads(path.read_text())

    if artifact_annotation.loadb is not None:
        return artifact_annotation.loadb(path.read_bytes())

    if artifact_annotation.loader == ArtifactLoader.json.value:
        with path.open() as f:
            return json.load(f)

    if artifact_annotation.loader == ArtifactLoader.file.value:
        return path.read_text()

    if artifact_annotation.loader is None:
        return artifact_annotation.path

    raise RuntimeError(f"Artifact {artifact_annotation.name} was not given a value")


T = TypeVar("T", bound=Type[BaseModel])


def map_runner_input(
    runner_input_class: T,
    kwargs: Dict[str, str],
) -> T:
    """Map argo input kwargs to the fields of the given Input, return an instance of the class.

    If the field is annotated, we look for the kwarg with the name from the annotation (Parameter or Artifact).
    Otherwise, we look for the kwarg with the name of the field.
    """
    input_model_obj = {}

    def load_parameter_value(
        value: str,
        value_type: type,
        loader: Optional[Callable[[str], Any]] = None,
    ) -> Any:
        if origin_type_issubtype(value_type, (str, NoneType)):
            return value

        if loader is not None:
            return load_param_input(value, loader)

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    runner_input_annotations = get_field_annotations(runner_input_class)

    def map_field(
        field: str,
        kwargs: Dict[str, str],
    ) -> Any:
        annotation = runner_input_annotations.get(field)
        assert annotation is not None, "Input fields must be type-annotated"  # Note: not necessarily with `Annotated`
        ann_type = unwrap_annotation(annotation)

        if param_or_artifact := get_workflow_annotation(annotation):
            if isinstance(param_or_artifact, Parameter):
                assert not param_or_artifact.output
                return load_parameter_value(
                    get_annotated_input_param(field, param_or_artifact, kwargs),
                    ann_type,
                    param_or_artifact.loads,
                )
            else:
                return get_annotated_artifact_value(field, param_or_artifact)
        else:
            return load_parameter_value(kwargs[field], ann_type)

    for field in get_fields(runner_input_class):
        input_model_obj[field] = map_field(field, kwargs)

    return cast(T, runner_input_class.parse_obj(input_model_obj))


def _save_annotated_return_outputs(
    function_outputs: Union[Tuple[Any], Any],
    output_annotations: List[Union[Tuple[type, Union[Parameter, Artifact]], Union[Type[OutputV1], Type[OutputV2]]]],
) -> Optional[Union[OutputV1, OutputV2]]:
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
        if isinstance(output_value, (OutputV1, OutputV2)):
            if os.environ.get("hera__script_pydantic_io", None) is None:
                raise ValueError("hera__script_pydantic_io environment variable is not set")

            return_obj = output_value

            for field, value in output_value.dict().items():
                if field in {"exit_code", "result"}:
                    continue

                matching_output = output_value._get_output(field)
                path = _get_outputs_path(matching_output)
                _write_to_path(path, value, _get_dumper_function(matching_output))
        else:
            assert isinstance(dest, tuple)

            type_ = get_unsubscripted_type(dest[0])
            if not isinstance(output_value, type_):
                raise ValueError(
                    f"The type of output `{dest[1].name}`, `{type(output_value)}` does not match the annotated type `{dest[0]}`"
                )

            if not dest[1].name:
                raise ValueError("The name was not provided for one of the outputs.")

            path = _get_outputs_path(dest[1])
            _write_to_path(path, output_value, _get_dumper_function(dest[1]))

    if os.environ.get("hera__script_pydantic_io", None) is not None:
        return return_obj

    return None


def _save_dummy_outputs(
    output_annotations: List[
        Union[
            Tuple[type, Union[Parameter, Artifact]],
            Union[Type[OutputV1], Type[OutputV2]],
        ]
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
        if isinstance(dest, type) and issubclass(dest, (OutputV1, OutputV2)):
            if os.environ.get("hera__script_pydantic_io", None) is None:
                raise ValueError("hera__script_pydantic_io environment variable is not set")

            for field in get_fields(dest):
                if field in {"exit_code", "result"}:
                    continue

                annotation = dest._get_output(field)
                path = _get_outputs_path(annotation)
                _write_to_path(path, "")
        else:
            assert isinstance(dest, tuple)
            if not dest[1].name:
                raise ValueError("The name was not provided for one of the outputs.")

            path = _get_outputs_path(dest[1])
            _write_to_path(path, "")


def _write_to_path(path: Path, output_value: Any, dumper: Callable = serialize) -> None:
    """Write the output_value as serialized text to the provided path. Create the necessary parent directories."""
    dumped_output = dumper(output_value)
    if dumped_output is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(dumped_output, str):
            path.write_text(dumped_output)
        elif isinstance(dumped_output, bytes):
            path.write_bytes(dumped_output)
