import sys
from typing import TYPE_CHECKING, Iterator, List, Optional, Tuple, Type, Union

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


from hera.shared._pydantic import _PYDANTIC_VERSION, FieldInfo, get_field_annotations, get_fields
from hera.shared._type_util import construct_io_from_annotation, get_workflow_annotation
from hera.shared.serialization import MISSING, serialize
from hera.workflows._context import _context
from hera.workflows.artifact import Artifact
from hera.workflows.models import (
    Arguments as ModelArguments,
    Artifact as ModelArtifact,
    Parameter as ModelParameter,
    ValueFrom,
)
from hera.workflows.parameter import Parameter

if _PYDANTIC_VERSION == 2:
    from pydantic import BaseModel as V2BaseModel
    from pydantic.v1 import BaseModel as V1BaseModel
    from pydantic_core import PydanticUndefined
else:
    from pydantic import BaseModel as V1BaseModel  # type: ignore[assignment]

    V2BaseModel = V1BaseModel  # type: ignore
    PydanticUndefined = None  # type: ignore[assignment]

if TYPE_CHECKING:
    # We add BaseModel as a parent class of the mixins only when type checking which allows it
    # to be used with either a V1 BaseModel or a V2 BaseModel
    from hera.shared._pydantic import PydanticBaseModel as BaseModel
else:
    # Subclassing `object` when using the real code (i.e. not type-checking) is basically a no-op
    BaseModel = object  # type: ignore


def _construct_io_from_fields(cls: Type[BaseModel]) -> Iterator[Tuple[str, FieldInfo, Union[Parameter, Artifact]]]:
    """Constructs a Parameter or Artifact object for all Pydantic fields based on their annotations.

    If a field has a Parameter or Artifact annotation, a copy will be returned, with missing
    fields filled out based on other metadata. Otherwise, a Parameter object will be constructed.
    """
    annotations = get_field_annotations(cls)
    for field, field_info in get_fields(cls).items():
        yield field, field_info, construct_io_from_annotation(field, annotations[field])


class InputMixin(BaseModel):
    def __new__(cls, **kwargs):
        if _context.declaring:
            # Intercept the declaration to avoid validation on the templated strings
            # We must then turn off declaring mode to be able to "construct" an instance
            # of the InputMixin subclass.
            _context.declaring = False
            instance = cls.construct(**kwargs)
            _context.declaring = True
            return instance
        else:
            return super(InputMixin, cls).__new__(cls)

    def __init__(self, /, **kwargs):
        if _context.declaring:
            # Return in order to skip validation of `construct`ed instance
            return

        super().__init__(**kwargs)

    @classmethod
    def _get_parameters(cls, object_override: Optional[Self] = None) -> List[Parameter]:
        parameters = []

        for field, field_info, param in _construct_io_from_fields(cls):
            if isinstance(param, Parameter):
                if param.default is not None:
                    raise ValueError(
                        "default cannot be set via the Parameter's default, use a Python default value instead."
                    )
                if object_override:
                    param.default = serialize(getattr(object_override, field))
                elif field_info.default is not None and field_info.default != PydanticUndefined:  # type: ignore
                    # Serialize the value (usually done in Parameter's validator)
                    param.default = serialize(field_info.default)  # type: ignore
                parameters.append(param)

        return parameters

    @classmethod
    def _get_artifacts(cls, add_missing_path: bool = False) -> List[Artifact]:
        artifacts = []

        for _, _, artifact in _construct_io_from_fields(cls):
            if isinstance(artifact, Artifact):
                if add_missing_path and artifact.path is None:
                    artifact.path = artifact._get_default_inputs_path()
                artifacts.append(artifact)
        return artifacts

    @classmethod
    def _get_inputs(cls, add_missing_path: bool = False) -> List[Union[Artifact, Parameter]]:
        return cls._get_artifacts(add_missing_path) + cls._get_parameters()

    @classmethod
    def _get_as_templated_arguments(cls) -> Self:
        """Returns the Input with templated values to propagate through a DAG/Steps function."""
        object_dict = {}

        for field, _, annotation in _construct_io_from_fields(cls):
            input_type = "parameters" if isinstance(annotation, Parameter) else "artifacts"
            object_dict[field] = "{{" + f"inputs.{input_type}.{annotation.name}" + "}}"

        return cls.construct(None, **object_dict)

    def _get_as_arguments(self) -> ModelArguments:
        params = []
        artifacts = []

        if isinstance(self, V1BaseModel):
            self_dict = self.dict()
        elif _PYDANTIC_VERSION == 2 and isinstance(self, V2BaseModel):
            self_dict = self.model_dump(warnings="none")

        for field, _, annotation in _construct_io_from_fields(type(self)):
            # The value may be a static value (of any time) if it has a default value, so we need to serialize it
            # If it is a templated string, it will be unaffected as `"{{mystr}}" == serialize("{{mystr}}")``
            templated_value = serialize(self_dict[field])
            name = annotation.name
            assert name is not None  # guaranteed by _get_workflow_annotations

            if isinstance(annotation, Parameter):
                params.append(ModelParameter(name=name, value=templated_value))
            else:
                artifacts.append(ModelArtifact(name=name, from_=templated_value))

        return ModelArguments(parameters=params or None, artifacts=artifacts or None)


class OutputMixin(BaseModel):
    def __new__(cls, **kwargs):
        if _context.declaring:
            # Intercept the declaration to avoid validation on the templated strings
            _context.declaring = False
            instance = cls.construct(**kwargs)
            _context.declaring = True
            return instance
        else:
            return super(OutputMixin, cls).__new__(cls)

    def __init__(self, /, **kwargs):
        if _context.declaring:
            # Return in order to skip validation of `construct`ed instance
            return

        super().__init__(**kwargs)

    @classmethod
    def _get_outputs(cls, add_missing_path: bool = False) -> List[Union[Artifact, Parameter]]:
        outputs: List[Union[Artifact, Parameter]] = []

        for field, field_info, annotation in _construct_io_from_fields(cls):
            if field in {"exit_code", "result"}:
                continue
            if isinstance(annotation, Parameter):
                if annotation.default is None:
                    default = field_info.default
                    if default is not None and default != PydanticUndefined:
                        annotation.default = serialize(default)

                if add_missing_path and (annotation.value_from is None or annotation.value_from.path is None):
                    annotation.value_from = ValueFrom(path=f"/tmp/hera-outputs/parameters/{annotation.name}")
            else:
                if add_missing_path and annotation.path is None:
                    annotation.path = f"/tmp/hera-outputs/artifacts/{annotation.name}"
            outputs.append(annotation)
        return outputs

    @classmethod
    def _get_output(cls, field_name: str) -> Union[Artifact, Parameter]:
        annotations = get_field_annotations(cls)
        annotation = annotations[field_name]
        if output := get_workflow_annotation(annotation):
            if not output.name:
                output.name = field_name
            return output

        # Create a Parameter from basic type annotations
        default = get_fields(cls)[field_name].default
        if default is None or default == PydanticUndefined:
            default = MISSING
        return Parameter(name=field_name, default=default)  # type: ignore

    def _get_as_invocator_output(self) -> List[Union[Artifact, Parameter]]:
        """Get the Output model as the output of a dag/steps template.

        This lets dags and steps hoist task/step outputs into its own outputs.
        """
        outputs: List[Union[Artifact, Parameter]] = []

        if isinstance(self, V1BaseModel):
            self_dict = self.dict()
        elif _PYDANTIC_VERSION == 2 and isinstance(self, V2BaseModel):
            self_dict = self.model_dump(warnings="none")

        for field, _, annotation in _construct_io_from_fields(type(self)):
            if field in {"exit_code", "result"}:
                continue

            templated_value = self_dict[field]  # a string such as `"{{tasks.task_a.outputs.parameter.my_param}}"`

            if isinstance(annotation, Parameter):
                annotation.value_from = ValueFrom(parameter=templated_value)
            else:
                annotation.from_ = templated_value

            outputs.append(annotation)

        return outputs
