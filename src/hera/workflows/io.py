"""Input/output models for the Hera runner. TODO move to hera.workflows.runner package."""
from typing import Any, List, Union

from hera.shared._pydantic import BaseModel
from hera.workflows.artifact import Artifact
from hera.workflows.parameter import Parameter

try:
    from typing import Annotated, get_args, get_origin  # type: ignore
except ImportError:
    from typing_extensions import Annotated, get_args, get_origin  # type: ignore


class RunnerInput(BaseModel):
    """Input model."""

    @classmethod
    def _get_inputs(cls) -> List[Union[Artifact, Parameter]]:
        inputs = []
        annotations = {k: v for k, v in cls.__annotations__.items()}

        for field in cls.__fields__:
            if get_origin(annotations[field]) is Annotated:
                if isinstance(get_args(annotations[field])[1], Parameter):
                    param = get_args(annotations[field])[1]
                    if cls.__fields__[field].default:
                        param.default = cls.__fields__[field].default
                    inputs.append(param)
                elif isinstance(get_args(annotations[field])[1], Artifact):
                    inputs.append(get_args(annotations[field])[1])
            else:
                # Create a Parameter from basic type annotations
                inputs.append(Parameter(name=field, default=cls.__fields__[field].default))
        return inputs


class RunnerOutput(BaseModel):
    """Output model."""

    exit_code: int = 0
    result: Any

    @classmethod
    def _get_outputs(cls) -> List[Union[Artifact, Parameter]]:
        outputs = []
        annotations = {k: v for k, v in cls.__annotations__.items() if k not in {"exit_code", "result"}}

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
