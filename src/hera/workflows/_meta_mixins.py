"""Build- and meta-related mixins that isolate shareable functionality between Hera objects."""

from __future__ import annotations

import functools
import inspect
from collections import ChainMap
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set, Type, TypeVar, Union, cast

from typing_extensions import ParamSpec

from hera._utils import type_util
from hera.shared import BaseMixin, global_config
from hera.shared._global_config import _DECORATOR_SYNTAX_FLAG, _flag_enabled
from hera.shared._pydantic import BaseModel, get_fields, root_validator
from hera.workflows._context import _context
from hera.workflows.exceptions import InvalidTemplateCall
from hera.workflows.io.v1 import (
    Input as InputV1,
    Output as OutputV1,
)
from hera.workflows.models import (
    Artifact as ModelArtifact,
    Parameter as ModelParameter,
    TemplateRef,
)
from hera.workflows.parameter import Parameter
from hera.workflows.protocol import TWorkflow

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
    from inspect import get_annotations  # type: ignore
except ImportError:
    from hera.shared._inspect import get_annotations  # type: ignore

try:
    from types import NoneType  # type: ignore
except ImportError:
    NoneType = type(None)  # type: ignore


if TYPE_CHECKING:
    from hera.workflows._mixins import TemplateMixin
    from hera.workflows.steps import Step
    from hera.workflows.task import Task

_yaml: Optional[ModuleType] = None
try:
    import yaml

    _yaml = yaml
except ImportError:
    _yaml = None


_varname_imported: bool = False
try:
    # user must install `hera[experimental]`
    from varname import ImproperUseError, varname

    _varname_imported = True
except ImportError:
    pass

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


class ExperimentalMixin(BaseMixin):
    _experimental_warning_message: str = (
        "Unable to instantiate {} since it is an experimental feature."
        " Please turn on experimental features by setting "
        '`hera.shared.global_config.experimental_features["{}"] = True`.'
        " Note that experimental features are unstable and subject to breaking changes."
    )

    _flag: str

    @root_validator(allow_reuse=True)
    def _check_enabled(cls, values):
        if not global_config.experimental_features[cls._flag]:
            raise ValueError(cls._experimental_warning_message.format(cls, cls._flag))
        return values


def _set_model_attr(model: BaseModel, attrs: List[str], value: Any):
    # The `attrs` list represents a path to an attribute in `model`, whose attributes
    # are BaseModels themselves. Therefore we use `getattr` to get a reference to the final
    # BaseModel set to `curr`, then call `setattr` on that BaseModel, using the last attribute
    # name in attrs, and the value passed in.
    curr: BaseModel = model
    for attr in attrs[:-1]:
        curr = getattr(curr, attr)

    setattr(curr, attrs[-1], value)


def _get_model_attr(model: BaseModel, attrs: List[str]) -> Any:
    # This is almost the same as _set_model_attr.
    # The `attrs` list represents a path to an attribute in `model`, whose attributes
    # are BaseModels themselves. Therefore we use `getattr` to get a reference to the final
    # BaseModel set to `curr`, then `getattr` on that BaseModel, using the last attribute
    # name in attrs.
    curr: BaseModel = model
    for attr in attrs[:-1]:
        curr = getattr(curr, attr)

    return getattr(curr, attrs[-1])


class ModelMapperMixin(BaseMixin):
    """`ModelMapperMixin` allows Hera classes to be mapped to auto-generated Argo classes."""

    class ModelMapper:
        def __init__(self, model_path: str, hera_builder: Optional[Callable] = None):
            self.model_path = None
            self.builder = hera_builder

            if not model_path:
                # Allows overriding parent attribute annotations to remove the mapping
                return

            self.model_path = model_path.split(".")
            curr_class: Type[BaseModel] = self._get_model_class()
            for key in self.model_path:
                fields = get_fields(curr_class)
                if key not in fields:
                    raise ValueError(f"Model key '{key}' does not exist in class {curr_class}")
                curr_class = fields[key].outer_type_  # type: ignore

        @classmethod
        def _get_model_class(cls) -> Type[BaseModel]:
            raise NotImplementedError

        @classmethod
        def build_model(
            cls, hera_class: Type[ModelMapperMixin], hera_obj: ModelMapperMixin, model: TWorkflow
        ) -> TWorkflow:
            assert isinstance(hera_obj, ModelMapperMixin)

            for attr, annotation in hera_class._get_all_annotations().items():
                if type_util.is_annotated(annotation) and (
                    mapper := type_util.consume_annotated_metadata(annotation, ModelMapperMixin.ModelMapper)
                ):
                    # Value comes from builder function if it exists on hera_obj, otherwise directly from the attr
                    value = (
                        getattr(hera_obj, mapper.builder.__name__)()
                        if mapper.builder is not None
                        else getattr(hera_obj, attr)
                    )
                    if value is not None:
                        _set_model_attr(model, mapper.model_path, value)

            return model

    @classmethod
    def _get_all_annotations(cls) -> ChainMap:
        """Gets all annotations of this class and any parent classes."""
        return ChainMap(*(get_annotations(c) for c in cls.__mro__))

    @classmethod
    def _from_model(cls, model: BaseModel) -> ModelMapperMixin:
        """Parse from given model to cls's type."""
        hera_obj = cls()

        for attr, annotation in cls._get_all_annotations().items():
            if type_util.is_annotated(annotation) and (
                mapper := type_util.consume_annotated_metadata(annotation, ModelMapperMixin.ModelMapper)
            ):
                if mapper.model_path:
                    value = _get_model_attr(model, mapper.model_path)
                    if value is not None:
                        setattr(hera_obj, attr, value)

        return hera_obj

    @classmethod
    def _from_dict(cls, model_dict: Dict, model: Type[BaseModel]) -> ModelMapperMixin:
        """Parse from given model_dict, using the given model type to call its parse_obj."""
        model_workflow = model.parse_obj(model_dict)
        return cls._from_model(model_workflow)

    @classmethod
    def from_dict(cls, model_dict: Dict) -> ModelMapperMixin:
        """Parse from given model_dict."""
        raise NotImplementedError

    @classmethod
    def _from_yaml(cls, yaml_str: str, model: Type[BaseModel]) -> ModelMapperMixin:
        """Parse from given yaml string, using the given model type to call its parse_obj."""
        if not _yaml:
            raise ImportError("PyYAML is not installed")
        return cls._from_dict(_yaml.safe_load(yaml_str), model)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> ModelMapperMixin:
        """Parse from given yaml_str."""
        raise NotImplementedError

    @classmethod
    def _from_file(cls, yaml_file: Union[Path, str], model: Type[BaseModel]) -> ModelMapperMixin:
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


def _get_param_items_from_source(source: Callable) -> List[Parameter]:
    """Returns a list (possibly empty) of `Parameter` from the specified `source`.

    This infers that each non-keyword, positional, argument of the given source is a parameter that stems from a
    fanout. Therefore, each parameter value takes the form of `{{item}}` when there's a single argument or
    `{{item.<argument name>}}` when there are other arguments.

    Returns:
    -------
    List[Parameter]
        A list of identified parameters (possibly empty).
    """
    source_signature: List[str] = []
    for p in inspect.signature(source).parameters.values():
        if p.default == inspect.Parameter.empty and p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            # only add positional or keyword arguments that are not set to a default value
            # as the default value ones are captured by the automatically generated `Parameter` fields for positional
            # kwargs. Otherwise, we assume that the user sets the value of the parameter via the `with_param` field
            source_signature.append(p.name)

    if len(source_signature) == 1:
        return [Parameter(name=n, value="{{item}}") for n in source_signature]
    return [Parameter(name=n, value=f"{{{{item.{n}}}}}") for n in source_signature]


def _get_params_from_items(with_items: List[Any]) -> Optional[List[Parameter]]:
    """Returns an optional list of `Parameter` from the specified list of `with_items`.

    The assembled list of `Parameter` contains all the unique parameters identified from the `with_items` list. For
    example, if the `with_items` list contains 3 serializable elements such as
    `[{'a': 1, 'b': 2}, {'a': 3, 'b': 4}, {'a': 5, 'b': 6}]`, then only 2 `Parameter`s are returned. Namely, only
     `Parameter(name='a')` and `Parameter(name='b')` is returned, with values `{{item.a}}` and `{{item.b}}`,
     respectively. This helps with the parallel/serial processing of the supplied items.
    """
    if len(with_items) == 0:
        return None
    elif len(with_items) == 1:
        el = with_items[0]
        if len(el.keys()) == 1:
            return [Parameter(name=n, value="{{item}}") for n in el.keys()]
        else:
            return [Parameter(name=n, value=f"{{{{item.{n}}}}}") for n in el.keys()]
    return [Parameter(name=n, value=f"{{{{item.{n}}}}}") for n in with_items[0].keys()]


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
        parameter_names = self._get_parameter_names(arguments)
        artifact_names = self._get_artifact_names(arguments)

        # when the `source` is set via an `@script` decorator, it does not come in with the `kwargs` so we need to
        # set it here in order for the following logic to capture it
        if "source" not in kwargs and hasattr(self, "source"):
            kwargs["source"] = self.source  # type: ignore

        if "source" in kwargs and "with_param" in kwargs:
            arguments += self._get_deduped_params_from_source(parameter_names, artifact_names, kwargs["source"])
        elif "source" in kwargs and "with_items" in kwargs:
            arguments += self._get_deduped_params_from_items(parameter_names, kwargs["with_items"])

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
                return Step(template=self, **kwargs)

            if isinstance(_context.pieces[-1], DAG):
                return Task(template=self, **kwargs)

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
        return {p.name for p in parameters}.union(
            set(functools.reduce(lambda x, y: cast(List[str], x) + list(y.keys()), keys, []))
        )

    def _get_artifact_names(self, arguments: List) -> Set[str]:
        """Returns the set of artifact names that are currently set on the mixin inheritor."""
        from hera.workflows.artifact import Artifact

        artifacts = [arg for arg in arguments if isinstance(arg, (ModelArtifact, Artifact))]
        return {a if isinstance(a, str) else a.name for a in artifacts if a.name}

    def _get_deduped_params_from_source(
        self, parameter_names: Set[str], artifact_names: Set[str], source: Callable
    ) -> List[Parameter]:
        """Infer arguments from the given source and deduplicates based on the given params and artifacts.

        Argo uses the `inputs` field to indicate the expected parameters of a specific template whereas the
        `arguments` are used to indicate exactly what _values_ are assigned to the set inputs. Here,
        we infer the arguments when `with_param` is used. If a source is passed along with `with_param`, we
        infer the arguments to set from the given source. It is assumed that `with_param` will return the
        expected result for Argo to fan out the task on.

        Parameters
        ----------
        parameter_names: Set[str]
            Set of already constructed parameter names.
        artifact_names: Set[str]
            Set of already constructed artifact names.
        source: Callable
            The source function to infer the arguments from.

        Returns:
        -------
        List[Parameter]
            The list of inferred arguments to set.
        """
        new_arguments = []
        new_parameters = _get_param_items_from_source(source)
        for p in new_parameters:
            if p.name not in parameter_names and p.name not in artifact_names:
                new_arguments.append(p)
        return new_arguments

    def _get_deduped_params_from_items(self, parameter_names: Set[str], items: List[Any]) -> List[Parameter]:
        """Infer arguments from the given items.

        The main difference between `with_items` and `with_param` is that param is a serialized version of
        `with_items`. Hence, `with_items` comes in the form of a list of objects, whereas `with_param` comes
        in as a single serialized object. Here, we can infer the parameters to create based on the content
        of `with_items`.

        Parameters
        ----------
        parameter_names: Set[str]
            Set of already constructed parameter names.
        items: List[Any]
            The items to infer the arguments from.

        Returns:
        -------
        List[Parameter]
            The list of inferred arguments to set.
        """
        item_params = _get_params_from_items(items)
        new_params = []
        if item_params is not None:
            for p in item_params:
                if p.name not in parameter_names:
                    new_params.append(p)
        return new_params


FuncIns = ParamSpec("FuncIns")  # For input types of given func to script decorator
FuncR = TypeVar("FuncR")  # For return type of given func to script decorator

PydanticKwargs = ParamSpec("PydanticKwargs")  # For input attributes of a Pydantic class
PydanticCls = TypeVar("PydanticCls")
StepIns = ParamSpec("StepIns")  # For input attributes of Step class
TaskIns = ParamSpec("TaskIns")  # For input attributes of Task class


def _add_type_hints(
    _pydantic_obj: Callable[PydanticKwargs, PydanticCls],
) -> Callable[
    ...,
    Callable[
        PydanticKwargs,  # this adds type hints to the underlying *library* function kwargs
        Callable[  # we will return a function that is a decorator
            [Callable[FuncIns, FuncR]],  # taking underlying *user* function
            Callable[FuncIns, FuncR],  # and returning it
        ],
    ],
]:
    """Adds type hints to the decorated function."""
    return lambda func: func


class HeraBuildObj:
    def __init__(self, subnode_type: str, output_class: Type[Union[OutputV1, OutputV2]]) -> None:
        self.subnode_type = subnode_type
        self.output_class = output_class


class TemplateDecoratorFuncsMixin(ContextMixin):
    from hera.workflows.container import Container
    from hera.workflows.dag import DAG
    from hera.workflows.script import Script
    from hera.workflows.steps import Steps

    @staticmethod
    def _check_if_enabled(decorator_name: str):
        if not _flag_enabled(_DECORATOR_SYNTAX_FLAG):
            raise ValueError(
                str(
                    "Unable to use {} decorator since it is an experimental feature."
                    " Please turn on experimental features by setting "
                    '`hera.shared.global_config.experimental_features["{}"] = True`.'
                    " Note that experimental features are unstable and subject to breaking changes."
                ).format(decorator_name, _DECORATOR_SYNTAX_FLAG)
            )
        if not _varname_imported:
            raise ImportError(
                "`varname` is not installed. Install `hera[experimental]` to bring in the extra dependency"
            )

    def _create_subnode(
        self,
        subnode_name: str,
        func: Callable,
        template: TemplateMixin,
        *args,
        **kwargs,
    ) -> Union[Step, Task]:
        from hera.workflows.cluster_workflow_template import ClusterWorkflowTemplate
        from hera.workflows.dag import DAG
        from hera.workflows.steps import Parallel, Step, Steps
        from hera.workflows.task import Task
        from hera.workflows.workflow_template import WorkflowTemplate

        subnode_args = None
        if len(args) == 1 and isinstance(args[0], (InputV1, InputV2)):
            subnode_args = args[0]._get_as_arguments()

        signature = inspect.signature(func)
        output_class = signature.return_annotation

        subnode: Union[Step, Task]

        assert _context.pieces

        template_ref = None
        _context.declaring = False
        if _context.pieces[0] != self and isinstance(self, WorkflowTemplate):
            # Using None for cluster_scope means it won't appear in the YAML spec (saving some bytes),
            # as cluster_scope=False is the default value
            template_ref = TemplateRef(
                name=self.name,
                template=template.name,
                cluster_scope=True if isinstance(self, ClusterWorkflowTemplate) else None,
            )
            # Set template to None as it cannot be set alongside template_ref
            template = None  # type: ignore

        if isinstance(_context.pieces[-1], (Steps, Parallel)):
            subnode = Step(
                name=subnode_name,
                template=template,
                template_ref=template_ref,
                arguments=subnode_args,
                **kwargs,
            )
        elif isinstance(_context.pieces[-1], DAG):
            subnode = Task(
                name=subnode_name,
                template=template,
                template_ref=template_ref,
                arguments=subnode_args,
                depends=" && ".join(sorted(_context.pieces[-1]._current_task_depends)) or None,
                **kwargs,
            )
            _context.pieces[-1]._current_task_depends.clear()

        subnode._build_obj = HeraBuildObj(subnode._subtype, output_class)
        _context.declaring = True
        return subnode

    @_add_type_hints(Script)  # type: ignore
    def script(self, **script_kwargs) -> Callable:
        """A decorator that wraps a function into a Script object.

        Using this decorator users can define a function that will be executed as a script in a container. Once the
        `Script` is returned users can use it as they generally use a `Script` e.g. as a callable inside a DAG or Steps.
        Note that invoking the function will result in the template associated with the script to be added to the
        workflow context, so users do not have to worry about that.

        Parameters
        ----------
        **script_kwargs
            Keyword arguments to be passed to the Script object.

        Returns:
        -------
        Callable
            Function wrapper that holds a `Script` and allows the function to be called to create a Step or Task if
            in a Steps or DAG context.
        """
        self._check_if_enabled("script")

        from hera.workflows.script import RunnerScriptConstructor, Script

        def script_decorator(func: Callable[FuncIns, FuncR]) -> Callable:
            """The internal decorator function.

            Parameters
            ----------
            func: Callable
                Function to wrap.

            Returns:
            -------
            Callable
                Callable that calls the `Script` object `__call__` method when in a Steps or DAG context,
                otherwise calls function itself.
            """
            # instance methods are wrapped in `staticmethod`. Hera can capture that type and extract the underlying
            # function for remote submission since it does not depend on any class or instance attributes, so it is
            # submittable
            if isinstance(func, staticmethod):
                source: Callable = func.__func__
            else:
                source = func

            # take the client-provided `name` if it is submitted, pop the name for otherwise there will be two
            # kwargs called `name`
            # otherwise populate the `name` from the function name
            name = script_kwargs.pop("name", source.__name__.replace("_", "-"))

            if "constructor" not in script_kwargs and "constructor" not in global_config._get_class_defaults(Script):
                script_kwargs["constructor"] = RunnerScriptConstructor()

            # Open (Workflow) context to add `Script` object automatically
            with self:
                script_template = Script(name=name, source=source, **script_kwargs)

            if not isinstance(script_template.constructor, RunnerScriptConstructor):
                raise ValueError(f"Script '{name}' must use RunnerScriptConstructor")

            @functools.wraps(func)
            def script_call_wrapper(*args, **kwargs) -> Union[FuncR, Step, Task, None]:
                """Invokes a CallableTemplateMixin's `__call__` method using the given SubNode (Step or Task) args/kwargs."""
                if _context.declaring:
                    try:
                        # ignore decorator function assignment
                        subnode_name = varname()
                    except ImproperUseError:
                        # Template is being used without variable assignment (so use function name or provided name)
                        subnode_name = script_template.name  # type: ignore

                    subnode_name = kwargs.pop("name", subnode_name)
                    assert isinstance(subnode_name, str)

                    return self._create_subnode(subnode_name, func, script_template, *args, **kwargs)

                if _context.pieces:
                    return script_template.__call__(*args, **kwargs)
                return func(*args, **kwargs)

            # Set the wrapped function to the original function so that we can use it later
            script_call_wrapper.wrapped_function = func  # type: ignore
            # Set the template name to the inferred name
            script_call_wrapper.template_name = name  # type: ignore

            return script_call_wrapper

        return script_decorator

    @_add_type_hints(Container)  # type: ignore
    def container(self, **container_kwargs) -> Callable:
        self._check_if_enabled("container")
        from hera.workflows.container import Container

        def container_decorator(func: Callable[FuncIns, FuncR]) -> Callable:
            name = container_kwargs.pop("name", func.__name__.replace("_", "-"))

            signature = inspect.signature(func)
            func_inputs = signature.parameters
            inputs = []
            if len(func_inputs) >= 1:
                input_arg = list(func_inputs.values())[0].annotation
                if issubclass(input_arg, (InputV1, InputV2)):
                    inputs = input_arg._get_inputs()

            func_return = signature.return_annotation
            outputs = []
            if func_return and issubclass(func_return, (OutputV1, OutputV2)):
                outputs = func_return._get_outputs(add_missing_path=True)

            # Open context to add `Container` object automatically
            with self:
                container_template = Container(
                    name=name,
                    inputs=inputs,
                    outputs=outputs,
                    **container_kwargs,
                )

            @functools.wraps(func)
            def container_call_wrapper(*args, **kwargs) -> Union[FuncR, Step, Task, None]:
                """Invokes a CallableTemplateMixin's `__call__` method using the given SubNode (Step or Task) args/kwargs."""
                if _context.declaring:
                    try:
                        # ignore decorator function assignment
                        subnode_name = varname()
                    except ImproperUseError:
                        # Template is being used without variable assignment (so use function name or provided name)
                        subnode_name = container_template.name  # type: ignore

                    subnode_name = kwargs.pop("name", subnode_name)
                    assert isinstance(subnode_name, str)

                    return self._create_subnode(subnode_name, func, container_template, *args, **kwargs)

                if _context.pieces:
                    return container_template.__call__(*args, **kwargs)
                return func(*args, **kwargs)

            # Set the template name to the inferred name
            container_call_wrapper.template_name = name  # type: ignore

            return container_call_wrapper

        return container_decorator

    def _construct_invocator_decorator(
        self,
        invocator_type: Type[Union[Steps, DAG]],
        **template_kwargs,
    ):
        def decorator(func: Callable[FuncIns, FuncR]) -> Callable:
            """The decorating function that runs at "definition" time.

            This function will do 3 things:
            1. Inspect the function signature to get inputs/outputs
            2. Create the DAG/Steps template and add it to the workflow
            3. Run `func` in "declaring" mode to gather the tasks/steps and inputs/outputs between them, explained below.

            To run the function in declaring mode, we first need to create an input object which will
            carry templated string arguments in its attributes, rather than the correct types (like ints,
            other BaseModels, etc). This will let the templated strings propagate to the task arguments. We
            must skip Pydantic's validation of the input object, which is why InputMixin overrides __new__,
            to `construct` an instance; __init__ then returns early to skip validation.

            Then, passing in the object, we call the underlying function. This is where other templates
            are called, such as scripts, containers or other DAGs, and results in `Task` (or `Step`) objects being
            created. These tasks may have attribute access on them when passing values between tasks, as the
            code author sees Inputs/Outputs, while we are seeing Tasks in declaring mode. Therefore,
            TemplateInvocatorSubNodeMixin overrides __getattribute__, which, when in declaring mode, will
            retrieve a templated string for the given attribute, e.g. `my_task.an_output_param` will get
            the string "{{tasks.my_task.outputs.parameters.an_output_param}}". This also works for artifacts
            and the special `result` output.

            Finally, for the return from the function, a user may specify a subclass of Output. OutputMixin
            therefore also overrides __new__ and __init__ to allow an instance to be constructed without
            validation. We take this output object and convert it to a list of Artifacts/Parameters, setting
            the outputs of the template.
            """
            name = template_kwargs.pop("name", func.__name__.replace("_", "-"))

            signature = inspect.signature(func)
            func_inputs = signature.parameters
            inputs = []
            if len(func_inputs) == 1:
                arg_class = list(func_inputs.values())[0].annotation
                if issubclass(arg_class, (InputV1, InputV2)):
                    inputs = arg_class._get_inputs()

            func_return = signature.return_annotation
            outputs = []
            if func_return and issubclass(func_return, (OutputV1, OutputV2)):
                outputs = func_return._get_outputs()

            # Add dag/steps to workflow
            with self:
                template = invocator_type(
                    name=name,
                    inputs=inputs,
                    outputs=outputs,
                    **template_kwargs,
                )

            @functools.wraps(func)
            def call_wrapper(*args, **kwargs):
                if _context.declaring:
                    # A sub-dag as a Step or Task is being created
                    try:
                        subnode_name = varname()
                    except ImproperUseError:
                        # Template is being used without variable assignment (so use function name or provided name)
                        subnode_name = name

                    subnode_name = kwargs.pop("name", subnode_name)
                    assert isinstance(subnode_name, str)

                    return self._create_subnode(subnode_name, func, template, *args, **kwargs)

                return func(*args, **kwargs)

            call_wrapper.template_name = name  # type: ignore

            # Open workflow context to cross-check task template names
            with self, template:
                if len(func_inputs) == 1:
                    arg_class = list(func_inputs.values())[0].annotation
                    if issubclass(arg_class, (InputV1, InputV2)):
                        input_obj = arg_class._get_as_templated_arguments()
                        # "run" the dag/steps function to collect the tasks/steps
                        _context.declaring = True
                        func_return = func(input_obj)
                        _context.declaring = False

                        if func_return and isinstance(func_return, (OutputV1, OutputV2)):
                            template.outputs = func_return._get_as_invocator_output()

            return call_wrapper

        return decorator

    @_add_type_hints(DAG)  # type: ignore
    def dag(self, **dag_kwargs) -> Callable:
        self._check_if_enabled("dag")

        from hera.workflows.dag import DAG

        return self._construct_invocator_decorator(DAG, **dag_kwargs)

    @_add_type_hints(Steps)  # type: ignore
    def steps(self, **steps_kwargs) -> Callable:
        self._check_if_enabled("steps")

        from hera.workflows.steps import Steps

        return self._construct_invocator_decorator(Steps, **steps_kwargs)
