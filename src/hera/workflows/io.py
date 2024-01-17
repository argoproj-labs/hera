"""Input/output models for the Hera runner. TODO move to hera.workflows.runner package."""
from collections import ChainMap
from typing import Any, Dict, List, Tuple, Type, Union

from hera.shared._pydantic import BaseModel
from hera.workflows.artifact import Artifact
from hera.workflows.parameter import Parameter

try:
    from inspect import get_annotations  # type: ignore
except ImportError:
    from hera.workflows._inspect import get_annotations  # type: ignore

try:
    from typing import Annotated, get_args, get_origin  # type: ignore
except ImportError:
    from typing_extensions import Annotated, get_args, get_origin  # type: ignore


def _is_annotated_as(annotation: Any, class_or_tuple: Union[Type, Tuple[Type, ...]]):
    return get_origin(annotation) is Annotated and isinstance(get_args(annotation)[1], class_or_tuple)


class RunnerInput(BaseModel):
    """Input model."""

    @classmethod
    def _get_parameters(cls) -> List[Parameter]:
        parameters = []
        annotations = {k: v for k, v in ChainMap(*(get_annotations(c) for c in cls.__mro__)).items()}

        for field in cls.__fields__:
            if get_origin(annotations[field]) is Annotated:
                if isinstance(get_args(annotations[field])[1], Parameter):
                    param = get_args(annotations[field])[1]
                    if cls.__fields__[field].default:
                        param.default = cls.__fields__[field].default
                    parameters.append(param)
            else:
                # Create a Parameter from basic type annotations
                parameters.append(Parameter(name=field, default=cls.__fields__[field].default))
        return parameters

    @classmethod
    def _get_artifacts(cls) -> List[Artifact]:
        artifacts = []
        annotations = {k: v for k, v in ChainMap(*(get_annotations(c) for c in cls.__mro__)).items()}

        for field in cls.__fields__:
            if get_origin(annotations[field]) is Annotated:
                if isinstance(get_args(annotations[field])[1], Artifact):
                    artifact = get_args(annotations[field])[1]
                    if artifact.path is None:
                        artifact.path = artifact._get_default_inputs_path()
                    artifacts.append(artifact)
        return artifacts


class RunnerOutput(BaseModel):
    """Output model."""

    exit_code: int = 0
    result: Any

    @classmethod
    def _get_outputs(cls) -> List[Union[Artifact, Parameter]]:
        outputs = []
        annotations = {k: v for k, v in ChainMap(*(get_annotations(c) for c in cls.__mro__)).items()}

        for field in cls.__fields__:
            if field in {"exit_code", "result"}:
                continue
            if get_origin(annotations[field]) is Annotated:
                if isinstance(get_args(annotations[field])[1], (Parameter, Artifact)):
                    outputs.append(get_args(annotations[field])[1])
            else:
                # Create a Parameter from basic type annotations
                outputs.append(Parameter(name=field, default=cls.__fields__[field].default))
        return outputs

    @classmethod
    def _get_output(cls, field_name: str) -> Union[Artifact, Parameter]:
        annotations = {k: v for k, v in ChainMap(*(get_annotations(c) for c in cls.__mro__)).items()}
        annotation = annotations[field_name]
        if get_origin(annotation) is Annotated:
            if isinstance(get_args(annotation)[1], (Parameter, Artifact)):
                return get_args(annotation)[1]

        # Create a Parameter from basic type annotations
        return Parameter(name=field_name, default=cls.__fields__[field_name].default)

    @classmethod
    def replace_keys(cls, obj: Dict) -> Dict:
        """Replaces keys in obj with Annotated Parameter/Artifact names for Argo."""
        for key, annotation in ChainMap(*(get_annotations(c) for c in cls.__mro__)).items():
            if key in {"exit_code", "result"} or not _is_annotated_as(annotation, (Artifact, Parameter)):
                continue
            argo_name = get_args(annotation)[1].name

            obj[argo_name] = obj[key]
            del obj[key]
        return obj
