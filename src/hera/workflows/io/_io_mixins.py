from typing import TYPE_CHECKING, Any, List, Optional, Union

from hera.shared._pydantic import _PYDANTIC_VERSION, get_field_annotations, get_fields
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


try:
    from typing import Annotated, Self, get_args, get_origin  # type: ignore
except ImportError:
    from typing_extensions import Annotated, Self, get_args, get_origin  # type: ignore

if TYPE_CHECKING:
    # We add BaseModel as a parent class of the mixins only when type checking which allows it
    # to be used with either a V1 BaseModel or a V2 BaseModel
    from pydantic import BaseModel
else:
    # Subclassing `object` when using the real code (i.e. not type-checking) is basically a no-op
    BaseModel = object  # type: ignore


_varname_imported: bool = False
try:
    from varname import argname

    _varname_imported = True
except ImportError:
    pass


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
        annotations = get_field_annotations(cls)

        for field, field_info in get_fields(cls).items():
            if get_origin(annotations[field]) is Annotated:
                # Copy so as to not modify the Input fields themselves
                param = get_args(annotations[field])[1].copy()
                if isinstance(param, Parameter):
                    if param.name is None:
                        param.name = field
                    if object_override:
                        param.default = serialize(getattr(object_override, field))
                    elif field_info.default is not None and field_info.default != PydanticUndefined:  # type: ignore
                        # Serialize the value (usually done in Parameter's validator)
                        param.default = serialize(field_info.default)  # type: ignore
                    parameters.append(param)
            else:
                # Create a Parameter from basic type annotations
                default = getattr(object_override, field) if object_override else field_info.default

                # For users on Pydantic 2 but using V1 BaseModel, we still need to check if `default` is None
                if default is None or default == PydanticUndefined:
                    default = MISSING

                parameters.append(Parameter(name=field, default=default))

        return parameters

    @classmethod
    def _get_artifacts(cls) -> List[Artifact]:
        artifacts = []
        annotations = get_field_annotations(cls)

        for field in get_fields(cls):
            if get_origin(annotations[field]) is Annotated:
                # Copy so as to not modify the Input fields themselves
                artifact = get_args(annotations[field])[1].copy()
                if isinstance(artifact, Artifact):
                    if artifact.name is None:
                        artifact.name = field
                    if artifact.path is None:
                        artifact.path = artifact._get_default_inputs_path()
                    artifacts.append(artifact)
        return artifacts

    @classmethod
    def _get_inputs(cls) -> List[Union[Artifact, Parameter]]:
        return cls._get_artifacts() + cls._get_parameters()

    @classmethod
    def _get_as_templated_arguments(cls) -> Self:
        """Returns the Input with templated values to propagate through a DAG/Steps function."""
        object_dict = {}
        cls_fields = get_fields(cls)
        annotations = get_field_annotations(cls)

        for field in cls_fields:
            if get_origin(annotations[field]) is Annotated:
                annotation = get_args(annotations[field])[1]
                if isinstance(annotation, (Artifact, Parameter)):
                    name = annotation.name
                    if isinstance(annotation, Parameter):
                        object_dict[field] = "{{inputs.parameters." + f"{name}" + "}}"
                    elif isinstance(annotation, Artifact):
                        object_dict[field] = "{{inputs.artifacts." + f"{name}" + "}}"
            else:
                object_dict[field] = "{{inputs.parameters." + f"{field}" + "}}"

        return cls.construct(None, **object_dict)

    def _get_as_arguments(self) -> ModelArguments:
        params = []
        artifacts = []
        annotations = get_field_annotations(type(self))

        if isinstance(self, V1BaseModel):
            self_dict = self.dict()
        elif _PYDANTIC_VERSION == 2 and isinstance(self, V2BaseModel):
            self_dict = self.model_dump()

        for field in get_fields(type(self)):
            # The value may be a static value (of any time) if it has a default value, so we need to serialize it
            # If it is a templated string, it will be unaffected as `"{{mystr}}" == serialize("{{mystr}}")``
            templated_value = serialize(self_dict[field])

            if get_origin(annotations[field]) is Annotated:
                annotation = get_args(annotations[field])[1]
                if isinstance(annotation, Parameter) and annotation.name:
                    params.append(ModelParameter(name=annotation.name, value=templated_value))
                elif isinstance(annotation, Artifact) and annotation.name:
                    artifacts.append(ModelArtifact(name=annotation.name, from_=templated_value))
            else:
                params.append(ModelParameter(name=field, value=templated_value))

        return ModelArguments(parameters=params or None, artifacts=artifacts or None)


class PathGetter:
    def __init__(self, path: str):
        self.path = path


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
    def path(cls, attribute: Any) -> str:
        """Gets the path of the given attribute, given it is annotated as a Parameter or Artifact."""
        if not _varname_imported:
            raise ImportError(
                "`varname` is not installed. Install `hera[experimental]` to bring in the extra dependency"
            )

        attribute_name = argname("attribute")
        annotations = get_field_annotations(cls)

        if get_origin(annotations[attribute_name]) is not Annotated:
            raise SyntaxError("Cannot get path of non-Annotated attribute")

        annotation = get_args(annotations[attribute_name])[1]
        if not isinstance(annotation, (Parameter, Artifact)):
            raise SyntaxError("Cannot get path of non-Parameter or Artifact annotation")

        if isinstance(annotation, Parameter):
            return annotation.value_from.path

        if isinstance(annotation, Artifact):
            return annotation.path

        raise NotImplementedError("Unreachable code")

    @classmethod
    def _get_outputs(cls) -> List[Union[Artifact, Parameter]]:
        outputs = []
        annotations = get_field_annotations(cls)

        model_fields = get_fields(cls)

        for field in model_fields:
            if field in {"exit_code", "result"}:
                continue
            if get_origin(annotations[field]) is Annotated:
                if isinstance(get_args(annotations[field])[1], (Parameter, Artifact)):
                    outputs.append(get_args(annotations[field])[1])
            else:
                # Create a Parameter from basic type annotations
                default = model_fields[field].default
                if default is None or default == PydanticUndefined:
                    default = MISSING
                outputs.append(Parameter(name=field, default=default))
        return outputs

    @classmethod
    def _get_output(cls, field_name: str) -> Union[Artifact, Parameter]:
        annotations = get_field_annotations(cls)
        annotation = annotations[field_name]
        if get_origin(annotation) is Annotated:
            if isinstance(get_args(annotation)[1], (Parameter, Artifact)):
                return get_args(annotation)[1]

        # Create a Parameter from basic type annotations
        default = get_fields(cls)[field_name].default
        if default is None or default == PydanticUndefined:
            default = MISSING
        return Parameter(name=field_name, default=default)  # type: ignore

    def _get_as_output(self) -> List[Union[Artifact, Parameter]]:
        """Get the Output model as the output of a dag/steps template.

        This lets dags and steps hoist task/step outputs into its own outputs.
        """
        outputs: List[Union[Artifact, Parameter]] = []
        annotations = get_field_annotations(type(self))

        if isinstance(self, V1BaseModel):
            self_dict = self.dict()
        elif _PYDANTIC_VERSION == 2 and isinstance(self, V2BaseModel):
            self_dict = self.model_dump()

        for field in get_fields(type(self)):
            if field in {"exit_code", "result"}:
                continue

            templated_value = self_dict[field]  # a string such as `"{{tasks.task_a.outputs.parameter.my_param}}"`

            if get_origin(annotations[field]) is Annotated:
                annotation = get_args(annotations[field])[1]
                if isinstance(annotation, Parameter) and annotation.name:
                    outputs.append(Parameter(name=annotation.name, value_from=ValueFrom(parameter=templated_value)))
                elif isinstance(annotation, Artifact) and annotation.name:
                    outputs.append(Artifact(name=annotation.name, from_=templated_value))
            else:
                outputs.append(Parameter(name=field, value_from=ValueFrom(parameter=templated_value)))

        return outputs
