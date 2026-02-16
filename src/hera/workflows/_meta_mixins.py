"""Build- and meta-related mixins that isolate shareable functionality between Hera objects."""

from __future__ import annotations

import functools
import inspect
import sys
from collections import ChainMap
from dataclasses import dataclass
from inspect import get_annotations
from pathlib import Path
from types import ModuleType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
    cast,
)

from hera.shared import BaseMixin, global_config
from hera.shared._pydantic import APIBaseModel, get_fields
from hera.shared._type_util import construct_io_from_annotation, get_annotated_metadata, unwrap_annotation
from hera.workflows._context import _context
from hera.workflows.exceptions import InvalidTemplateCall
from hera.workflows.io.v2 import (
    Input as InputV2,
    Output as OutputV2,
)
from hera.workflows.models import (
    Artifact as ModelArtifact,
    Parameter as ModelParameter,
)
from hera.workflows.parameter import Parameter
from hera.workflows.protocol import Templatable, TWorkflow

if sys.version_info >= (3, 14):
    from hera.workflows.io.v2 import (
        Input as InputV1,
        Output as OutputV1,
    )
else:
    from hera.workflows.io.v1 import (
        Input as InputV1,
        Output as OutputV1,
    )

if TYPE_CHECKING:
    from hera.workflows.steps import Step
    from hera.workflows.task import Task

_yaml: Optional[ModuleType] = None
try:
    # user must install `hera[yaml]`
    import yaml

    _yaml = yaml
except ImportError:
    _yaml = None


THookable = TypeVar("THookable", bound="HookMixin")
"""`THookable` is the type associated with mixins that provide the ability to apply hooks from the global config"""

TContext = TypeVar("TContext", bound="ContextMixin")
"""`TContext` is the bounded context controlled by the context mixin that enable context management in workflow/dag"""


class ContextMixin(BaseMixin):
    """`ContextMixin` provides the ability to implement context management.

    The mixin implements the `__enter__` and `__exit__` functionality that enables the core `with` clause. The mixin
    expects that inheritors implement the `_add_sub` functionality, which adds a node defined within the context to the
    main object context such as `Workflow`, `DAG`, or `ContainerSet`.
    """

    def __enter__(self: TContext) -> TContext:
        """Enter the context of the inheritor."""
        _context.enter(self)
        return self

    def __exit__(self, *_) -> None:
        """Leave the context of the inheritor."""
        _context.exit()

    def _add_sub(self, node: Any) -> Any:
        """Adds the supplied node to the context of the inheritor."""
        raise NotImplementedError()


def _set_model_attr(model: APIBaseModel, attrs: List[str], value: Any):
    # The `attrs` list represents a path to an attribute in `model`, whose attributes
    # are BaseModels themselves. Therefore we use `getattr` to get a reference to the final
    # APIBaseModel set to `curr`, then call `setattr` on that APIBaseModel, using the last attribute
    # name in attrs, and the value passed in.
    curr: APIBaseModel = model
    for attr in attrs[:-1]:
        curr = getattr(curr, attr)

    setattr(curr, attrs[-1], value)


def _get_model_attr(model: APIBaseModel, attrs: List[str]) -> Any:
    # This is almost the same as _set_model_attr.
    # The `attrs` list represents a path to an attribute in `model`, whose attributes
    # are BaseModels themselves. Therefore we use `getattr` to get a reference to the final
    # APIBaseModel set to `curr`, then `getattr` on that APIBaseModel, using the last attribute
    # name in attrs.
    curr: APIBaseModel = model
    for attr in attrs[:-1]:
        curr = getattr(curr, attr)

    return getattr(curr, attrs[-1])


class ModelMapperMixin:
    """`ModelMapperMixin` allows Hera classes to be mapped to auto-generated Argo classes."""

    class ModelMapper:
        def __init__(self, model_path: str, hera_builder: Optional[Callable] = None):
            self.model_path = []
            self.builder = hera_builder

            if not model_path:
                # Allows overriding parent attribute annotations to remove the mapping
                return

            self.model_path = model_path.split(".")
            curr_class: Type[APIBaseModel] = self._get_model_class()
            for key in self.model_path:
                fields = get_fields(curr_class)
                if key not in fields:
                    raise ValueError(f"Model key '{key}' does not exist in class {curr_class}")
                curr_class = fields[key].annotation  # type: ignore

        @classmethod
        def _get_model_class(cls) -> Type[APIBaseModel]:
            raise NotImplementedError

        @classmethod
        def build_model(
            cls, hera_class: Type[ModelMapperMixin], hera_obj: ModelMapperMixin, model: TWorkflow
        ) -> TWorkflow:
            for attr, annotation in hera_class._get_all_annotations().items():
                if mappers := get_annotated_metadata(annotation, ModelMapperMixin.ModelMapper):
                    if len(mappers) != 1:
                        raise ValueError("Expected only one ModelMapper")

                    # Value comes from builder function if it exists on hera_obj, otherwise directly from the attr
                    value = (
                        getattr(hera_obj, mappers[0].builder.__name__)()
                        if mappers[0].builder is not None
                        else getattr(hera_obj, attr)
                    )
                    if value is not None:
                        _set_model_attr(model, mappers[0].model_path, value)

            return model

    @classmethod
    def _get_all_annotations(cls) -> ChainMap:
        """Gets all annotations of this class and any parent classes."""
        return ChainMap(*(get_annotations(c) for c in cls.__mro__))

    @classmethod
    def _from_model(cls, model: APIBaseModel) -> ModelMapperMixin:
        """Parse from given model to cls's type."""
        hera_obj = cls()

        for attr, annotation in cls._get_all_annotations().items():
            if mappers := get_annotated_metadata(annotation, ModelMapperMixin.ModelMapper):
                if len(mappers) != 1:
                    raise ValueError("Expected only one model mapper")
                if mappers[0].model_path:
                    value = _get_model_attr(model, mappers[0].model_path)
                    if value is not None:
                        setattr(hera_obj, attr, value)

        return hera_obj

    @classmethod
    def _from_dict(cls, model_dict: Dict, model: Type[APIBaseModel]) -> ModelMapperMixin:
        """Parse from given model_dict, using the given model type to call its model_validate."""
        model_workflow = model.model_validate(model_dict)
        return cls._from_model(model_workflow)

    @classmethod
    def from_dict(cls, model_dict: Dict) -> ModelMapperMixin:
        """Parse from given model_dict."""
        raise NotImplementedError

    @classmethod
    def _from_yaml(cls, yaml_str: str, model: Type[APIBaseModel]) -> ModelMapperMixin:
        """Parse from given yaml string, using the given model type to call its model_validate."""
        if not _yaml:
            raise ImportError("PyYAML is not installed")
        return cls._from_dict(_yaml.safe_load(yaml_str), model)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> ModelMapperMixin:
        """Parse from given yaml_str."""
        raise NotImplementedError

    @classmethod
    def _from_file(cls, yaml_file: Union[Path, str], model: Type[APIBaseModel]) -> ModelMapperMixin:
        yaml_file = Path(yaml_file)
        return cls._from_yaml(yaml_file.read_text(encoding="utf-8"), model)

    @classmethod
    def from_file(cls, yaml_file: Union[Path, str]) -> ModelMapperMixin:
        """Parse from given yaml_file."""
        raise NotImplementedError


class HookMixin(BaseMixin):
    """`HookMixin` provides the ability to dispatch hooks set on the global config to any inheritors."""

    def _dispatch_hooks(self: THookable) -> THookable:
        """Dispatches the global hooks on the current object."""
        output = self
        for hook in global_config._get_pre_build_hooks(output):
            output = hook(output)
            if output is None:
                raise RuntimeError(
                    f"Pre-build hook {hook.__name__} returned None."
                    "Please ensure you are returning the output value from the hook."
                )
        return output


def _get_pydantic_input_type(source: Callable) -> Union[None, Type[InputV1], Type[InputV2]]:
    """Returns a Pydantic Input type for the source, if it is using Pydantic IO."""
    function_parameters = inspect.signature(source).parameters
    if len(function_parameters) != 1:
        return None
    parameter = next(iter(function_parameters.values()))
    parameter_type = unwrap_annotation(parameter.annotation)
    if not isinstance(parameter_type, type) or not issubclass(parameter_type, (InputV1, InputV2)):
        return None
    return parameter_type


def _get_unset_source_parameters_as_items(source: Callable) -> List[Parameter]:
    """Get a list of `Parameter` with their values set to corresponding templated item strings.

    We infer that each non-keyword, positional, argument of the given source function is a
    parameter that stems from a fanout. Therefore, each parameter value takes the form of
    `{{item}}` when there's a single argument or `{{item.<argument name>}}` when there are
    other arguments.

    Returns:
    -------
    List[Parameter]
        A list of identified parameters (possibly empty).
    """
    non_default_parameters: List[Parameter] = []
    if pydantic_input := _get_pydantic_input_type(source):
        for parameter in pydantic_input._get_parameters():
            if parameter.default is None:
                non_default_parameters.append(parameter)
    else:
        for p in inspect.signature(source).parameters.values():
            if p.default == inspect.Parameter.empty and p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                # only add positional or keyword arguments that are not set to a default value
                # as the default value ones are captured by the automatically generated `Parameter` fields for positional
                # kwargs. Otherwise, we assume that the user sets the value of the parameter via the `with_param` field
                io = construct_io_from_annotation(p.name, p.annotation)
                if isinstance(io, Parameter) and io.default is None and not io.output:
                    non_default_parameters.append(io)

    if len(non_default_parameters) == 1:
        non_default_parameters[0].value = "{{item}}"
    else:
        for param in non_default_parameters:
            param.value = "{{item." + str(param.name) + "}}"
    return non_default_parameters


def _get_parameters_used_in_with_items(with_items: Any) -> Optional[List[Parameter]]:
    """Get the optional list of Parameters used in with_items, with their values set to corresponding templated item strings.

    The assembled list of `Parameter` contains all the unique parameters identified from the `with_items` list. For
    example, if the `with_items` list contains 3 serializable elements such as
    `[{'a': 1, 'b': 2}, {'a': 3, 'b': 4}, {'a': 5, 'b': 6}]`, then only 2 `Parameter`s are returned. Namely, only
    `Parameter(name='a')` and `Parameter(name='b')` is returned, with values `{{item.a}}` and `{{item.b}}`,
    respectively. This helps with the parallel/serial processing of the supplied items. If the list is of
    plain values and not key-values, then `None` is returned as there are no parameter substitutions.
    """
    if not with_items:
        return None

    if isinstance(with_items[0], dict):
        if not all(isinstance(item, dict) for item in with_items):
            raise ValueError(
                "List must contain all dictionaries or no dictionaries. "
                "Alternatively, serialize the dictionaries with `hera.shared.serialization.serialize()`."
            )
        # Check all dictionaries have the same keys, values will be serialised so we don't consider them
        if not all(set(item.keys()) == set(with_items[0].keys()) for item in with_items[1:]):
            raise ValueError(
                "All dictionaries in with_items must have the same keys. "
                "Alternatively, serialize the dictionaries with `hera.shared.serialization.serialize()`."
            )

        # Create a Parameter for each key in the dictionaries
        # Special case for dictionary len 1 as the value is just the item itself
        if len(with_items[0]) == 1:
            param_name = list(with_items[0].keys())[0]
            return [Parameter(name=param_name, value="{{item}}")]

        # Just use first dictionary as we checked type and key equality above
        return [Parameter(name=key, value=f"{{{{item.{key}}}}}") for key in with_items[0].keys()]

    else:
        # Ensure no dictionaries in the list
        if any(isinstance(item, dict) for item in with_items):
            raise ValueError(
                "List must contain all dictionaries or no dictionaries. "
                "Alternatively, serialize the dictionaries with `hera.shared.serialization.serialize()`."
            )
    return None


@dataclass
class CallableTemplateMixin(BaseMixin):
    """`CallableTemplateMixin` provides the ability to 'call' the template like a regular Python function.

    The callable template implements the `__call__` method for the inheritor. The `__call__` method supports invoking
    the template as a regular Python function. The call must be executed within an active context, which is a
    `Workflow`, `DAG` or `Steps` context since the call optionally returns a `Step` or a `Task` depending on the active
    context (`None` for `Workflow`, `Step` for `Steps` and `Task` for `DAG`). Note that `Steps` also supports calling
    templates in a parallel steps context via using `Steps(...).parallel()`. When the call is executed and the template
    does not exist on the active context, i.e. the workflow, it is automatically added for the user. Note that invoking
    the same template multiple times does *not* result in the creation/addition of the same template to the active
    context/workflow. Rather, a union is performed, so space is saved for users on the templates field and templates are
    not duplicated.
    """

    def __call__(self, *args, **kwargs) -> Union[None, Step, Task]:
        if "name" not in kwargs:
            kwargs["name"] = self.name  # type: ignore

        arguments = self._get_arguments(**kwargs)
        parameter_argument_names = self._get_parameter_names(arguments)
        artifact_argument_names = self._get_artifact_names(arguments)

        if "with_param" in kwargs and hasattr(self, "source"):
            arguments += self._get_templated_source_args(
                parameter_argument_names,
                artifact_argument_names,
                self.source,  # type: ignore
            )
        elif "with_items" in kwargs and hasattr(self, "source"):
            arguments += self._get_templated_arguments_from_items(
                parameter_argument_names,
                kwargs["with_items"],
                self.source,  # type: ignore
            )

        # it is possible for the user to pass `arguments` via `kwargs` along with `with_param`. The `with_param`
        # additional parameters are inferred and have to be added to the `kwargs['arguments']`, otherwise
        # the step/task will miss adding them when building the final arguments
        kwargs["arguments"] = arguments

        from hera.workflows.dag import DAG
        from hera.workflows.script import Script
        from hera.workflows.steps import Parallel, Step, Steps
        from hera.workflows.task import Task
        from hera.workflows.workflow import Workflow

        if _context.pieces:
            if isinstance(_context.pieces[-1], Workflow):
                # Notes on callable templates under a Workflow:
                # * If the user calls a script directly under a Workflow (outside of a Steps/DAG) then we add the script
                #   template to the workflow and return None.
                # * Containers, ContainerSets and Data objects (i.e. subclasses of CallableTemplateMixin) are already
                #   added when initialized under the Workflow context so a callable doesn't make sense in that context,
                #   so we raise an InvalidTemplateCall exception.
                # * We do not currently validate the added templates to stop a user adding the same template multiple
                #   times, which can happen if "calling" the same script multiple times to add it to the workflow,
                #   or initializing a second `Container` exactly like the first.
                if isinstance(self, Script):
                    _context.add_sub_node(self)
                    return None

                raise InvalidTemplateCall(
                    f"Callable Template '{self.name}' is not callable under a Workflow"  # type: ignore
                )
            if isinstance(_context.pieces[-1], (Steps, Parallel)):
                return Step(template=cast(Templatable, self), **kwargs)

            if isinstance(_context.pieces[-1], DAG):
                return Task(template=cast(Templatable, self), **kwargs)

        raise InvalidTemplateCall(
            f"Callable Template '{self.name}' is not under a Workflow, Steps, Parallel, or DAG context"  # type: ignore
        )

    def _get_arguments(self, **kwargs) -> List:
        """Returns a list of arguments from the kwargs given to the template call."""
        kwargs_arguments = kwargs.get("arguments", [])
        kwargs_arguments = kwargs_arguments if isinstance(kwargs_arguments, List) else [kwargs_arguments]  # type: ignore
        return kwargs_arguments

    def _get_parameter_names(self, arguments: List) -> Set[str]:
        """Returns the union of parameter names from the given arguments' parameter objects and dictionary keys."""
        parameters = [arg for arg in arguments if isinstance(arg, (ModelParameter, Parameter))]
        keys = [arg for arg in arguments if isinstance(arg, dict)]
        return {cast(str, p.name) for p in parameters}.union(
            set(functools.reduce(lambda x, y: cast(List[str], x) + list(y.keys()), keys, []))
        )

    def _get_artifact_names(self, arguments: List) -> Set[str]:
        """Returns the set of artifact names that are currently set on the mixin inheritor."""
        from hera.workflows.artifact import Artifact

        artifacts = [arg for arg in arguments if isinstance(arg, (ModelArtifact, Artifact))]
        return {a.name for a in artifacts if a.name}

    def _get_templated_source_args(
        self,
        parameter_argument_names: Set[str],
        artifact_argument_names: Set[str],
        source: Callable,
    ) -> List[Parameter]:
        """Get list of inferred arguments to set from the given source.

        Argo uses the `inputs` field to indicate the expected parameters of a specific template whereas the
        `arguments` are used to indicate exactly what _values_ are assigned to the set inputs. Here,
        we infer the arguments when `with_param` is used. If a source is passed along with `with_param`, we
        infer the arguments to set from the given source. It is assumed that `with_param` will return the
        expected result for Argo to fan out the task on.

        Parameters
        ----------
        parameter_argument_names: Set[str]
            Set of parameter names already constructed from arguments passed in.
        artifact_argument_names: Set[str]
            Set of artifact names already constructed from arguments passed in.
        source: Callable
            The source function to infer the arguments from.

        Returns:
        -------
        List[Parameter]
            The list of inferred arguments to set.
        """
        new_arguments = []
        source_params_as_items = _get_unset_source_parameters_as_items(source)
        for p in source_params_as_items:
            if p.name not in parameter_argument_names and p.name not in artifact_argument_names:
                new_arguments.append(p)
        return new_arguments

    def _get_templated_arguments_from_items(
        self,
        parameter_argument_names: Set[str],
        items: Any,
        source: Callable,
    ) -> List[Parameter]:
        """Infer arguments from the given items.

        The main difference between `with_items` and `with_param` is that param is a serialized version of
        `with_items`. Hence, `with_items` comes in the form of a list of objects, whereas `with_param` comes
        in as a single serialized object. Here, we can infer the parameters to create based on the content
        of `with_items`.

        Parameters
        ----------
        parameter_names: Set[str]
            Set of already constructed parameter names.
        items: Any
            The items to infer the arguments from.
        source: Callable
            The source function to confirm parameter names from.

        Returns:
        -------
        List[Parameter]
            The list of inferred arguments to set.
        """
        item_params = _get_parameters_used_in_with_items(items)
        if item_params is None:
            return []

        source_param_names = {name for name in inspect.signature(source).parameters.keys()}
        new_params = []
        for p in item_params:
            if p.name not in source_param_names:
                raise ValueError(
                    f"Parameter '{p.name}' not found in source function '{source.__name__}' "
                    "(you may need to serialize the dictionaries with `hera.shared.serialization.serialize()`)"
                )

            if p.name not in parameter_argument_names:
                new_params.append(p)
        return new_params


class HeraBuildObj:
    def __init__(self, subnode_type: str, output_class: Type[Union[OutputV1, OutputV2]]) -> None:
        self.subnode_type = subnode_type
        self.output_class = output_class
