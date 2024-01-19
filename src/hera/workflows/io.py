"""Input/output models for the Hera runner."""
from collections import ChainMap
from typing import Any, List, Union

from hera.shared._pydantic import BaseModel
from hera.shared.serialization import serialize
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


class RunnerInput(BaseModel):
    """Input model usable by the Hera Runner.

    RunnerInput is a Pydantic model which users can create a subclass of. When a subclass
    of RunnerInput is used as a function parameter type, the Hera Runner will take the fields
    of the user's subclass to create template input parameters and artifacts. See the example
    for the script_pydantic_io experimental feature.
    """

    @classmethod
    def _get_parameters(cls) -> List[Parameter]:
        parameters = []
        annotations = {k: v for k, v in ChainMap(*(get_annotations(c) for c in cls.__mro__)).items()}

        for field in cls.__fields__:
            if get_origin(annotations[field]) is Annotated:
                if isinstance(get_args(annotations[field])[1], Parameter):
                    param = get_args(annotations[field])[1]
                    if cls.__fields__[field].default:
                        # Serialize the value (usually done in Parameter's validator)
                        param.default = serialize(cls.__fields__[field].default)
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
    """Output model usable by the Hera Runner.

    RunnerOutput is a Pydantic model which users can create a subclass of. When a subclass
    of RunnerOutput is used as a function return type, the Hera Runner will take the fields
    of the user's subclass to create template output parameters and artifacts. See the example
    for the script_pydantic_io experimental feature.
    """

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
