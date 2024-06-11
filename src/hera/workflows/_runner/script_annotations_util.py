"""The script_annotations_util module contains functionality for the script annotations feature when used with the runner."""

import inspect
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union, cast

from hera.shared._pydantic import BaseModel, get_field_annotations, get_fields
from hera.shared.serialization import serialize
from hera.workflows import Artifact, Parameter
from hera.workflows.artifact import ArtifactLoader
from hera.workflows.io.v1 import (
    Input as InputV1,
    Output as OutputV1,
)

try:
    from hera.workflows.io.v2 import (  # type: ignore
        Input as InputV2,
        Output as OutputV2,
    )
except ImportError:
    from hera.workflows.io.v1 import (  # type: ignore
        Input as InputV2,
        Output as OutputV2,
    )

try:
    from typing import Annotated, get_args, get_origin  # type: ignore
except ImportError:
    from typing_extensions import Annotated, get_args, get_origin  # type: ignore


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


def _get_annotated_input_param_value(
    func_param_name: str,
    param_annotation: Parameter,
    kwargs: Dict[str, str],
) -> str:
    if param_annotation.name in kwargs:
        return kwargs[param_annotation.name]

    if func_param_name in kwargs:
        return kwargs[func_param_name]

    raise RuntimeError(
        f"Parameter {param_annotation.name if param_annotation.name else func_param_name} was not given a value"
    )


def get_annotated_param_value(
    func_param_name: str,
    param_annotation: Parameter,
    kwargs: Dict[str, str],
) -> Union[Path, str]:
    """Get the value from a given function param and its annotation.

    If the parameter is an output, return the path it will write to.
    If the parameter is an input, return the string value from the kwargs dict,
    which could be from the param_annotation.name if given, or func_param_name.
    """
    if param_annotation.output:
        if param_annotation.value_from and param_annotation.value_from.path:
            path = Path(param_annotation.value_from.path)
        else:
            path = _get_outputs_path(param_annotation)
        # Automatically create the parent directory (if required)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    return _get_annotated_input_param_value(func_param_name, param_annotation, kwargs)


def get_annotated_artifact_value(artifact_annotation: Artifact) -> Union[Path, Any]:
    """Get the value of the given Artifact annotation.

    If the artifact is an output, return the path it will write to.
    If the artifact is an input, return the loaded value (json, path or string) using its ArtifactLoader.

    As Artifacts are always Annotated in function parameters, we don't need to consider
    the `kwargs` or the function parameter name.
    """
    if artifact_annotation.output:
        if artifact_annotation.path:
            path = Path(artifact_annotation.path)
        else:
            path = _get_outputs_path(artifact_annotation)
        # Automatically create the parent directory (if required)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    if not artifact_annotation.path:
        # Path is added to the spec automatically when built. As it isn't present in the annotation itself,
        # we need to add it back in for the runner.
        artifact_annotation.path = artifact_annotation._get_default_inputs_path()

    if artifact_annotation.loader == ArtifactLoader.json.value:
        path = Path(artifact_annotation.path)
        return json.load(path.open())

    if artifact_annotation.loader == ArtifactLoader.file.value:
        path = Path(artifact_annotation.path)
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
    from hera.workflows._runner.util import _get_type

    input_model_obj = {}

    def load_parameter_value(value: str, value_type: type) -> Any:
        if issubclass(_get_type(value_type), str):
            return value

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
        assert annotation is not None, "RunnerInput fields must be type-annotated"
        if get_origin(annotation) is Annotated:
            # my_field: Annotated[int, Parameter(...)]
            ann_type = get_args(annotation)[0]
            param_or_artifact = get_args(annotation)[1]
        else:
            # my_field: int
            ann_type = annotation
            param_or_artifact = None

        if isinstance(param_or_artifact, Parameter):
            assert not param_or_artifact.output
            return load_parameter_value(
                _get_annotated_input_param_value(field, param_or_artifact, kwargs),
                ann_type,
            )
        elif isinstance(param_or_artifact, Artifact):
            return get_annotated_artifact_value(param_or_artifact)
        else:
            return load_parameter_value(kwargs[field], ann_type)

    for field in get_fields(runner_input_class):
        input_model_obj[field] = map_field(field, kwargs)

    return cast(T, runner_input_class.parse_raw(json.dumps(input_model_obj)))


def _map_argo_inputs_to_function(function: Callable, kwargs: Dict[str, str]) -> Dict:
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

    for func_param_name, func_param in inspect.signature(function).parameters.items():
        if get_origin(func_param.annotation) is Annotated:
            func_param_annotation = get_args(func_param.annotation)[1]

            if isinstance(func_param_annotation, Parameter):
                mapped_kwargs[func_param_name] = get_annotated_param_value(
                    func_param_name, func_param_annotation, kwargs
                )
            elif isinstance(func_param_annotation, Artifact):
                mapped_kwargs[func_param_name] = get_annotated_artifact_value(func_param_annotation)
            else:
                mapped_kwargs[func_param_name] = kwargs[func_param_name]
        elif get_origin(func_param.annotation) is None and issubclass(func_param.annotation, (InputV1, InputV2)):
            mapped_kwargs[func_param_name] = map_runner_input(func_param.annotation, kwargs)
        else:
            mapped_kwargs[func_param_name] = kwargs[func_param_name]
    return mapped_kwargs


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
        if isinstance(dest, (OutputV1, OutputV2)):
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


def _write_to_path(path: Path, output_value: Any) -> None:
    """Write the output_value as serialized text to the provided path. Create the necessary parent directories."""
    output_string = serialize(output_value)
    if output_string is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output_string)
