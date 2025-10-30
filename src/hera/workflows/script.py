"""The `hera.workflows.script` module provides the Script class.

See <https://argoproj.github.io/argo-workflows/workflow-concepts/#script>
for more on scripts in Argo Workflows.
"""

import ast
import copy
import inspect
import sys
import textwrap
from abc import abstractmethod
from functools import wraps
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

if sys.version_info >= (3, 10):
    from types import NoneType
else:
    NoneType = type(None)


from typing_extensions import ParamSpec, get_args, get_origin

from hera.expr import g
from hera.shared import BaseMixin, global_config
from hera.shared._global_config import (
    _SCRIPT_PYDANTIC_IO_FLAG,
    _flag_enabled,
)
from hera.shared._pydantic import _PYDANTIC_VERSION, root_validator, validator
from hera.shared._type_util import (
    construct_io_from_annotation,
    get_workflow_annotation,
    is_annotated,
    is_subscripted,
    origin_type_issupertype,
    unwrap_annotation,
)
from hera.shared.serialization import serialize
from hera.workflows._context import _context
from hera.workflows._meta_mixins import CallableTemplateMixin
from hera.workflows._mixins import (
    ArgumentsT,
    ContainerMixin,
    EnvIOMixin,
    OneOrMany,
    ResourceMixin,
    TemplateMixin,
    VolumeMountMixin,
)
from hera.workflows.artifact import (
    Artifact,
)
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
from hera.workflows.models import (
    ContinueOn,
    EnvVar,
    Inputs as ModelInputs,
    Lifecycle,
    LifecycleHook,
    Outputs as ModelOutputs,
    ScriptTemplate as _ModelScriptTemplate,
    SecurityContext,
    Sequence as _ModelSequence,
    Template as _ModelTemplate,
    TemplateRef,
    ValueFrom,
)
from hera.workflows.parameter import Parameter
from hera.workflows.protocol import Templatable
from hera.workflows.steps import Step
from hera.workflows.task import Task
from hera.workflows.volume import _BaseVolume


class ScriptConstructor(BaseMixin):
    """A ScriptConstructor is responsible for generating the source code for a Script given a python callable.

    This allows users to customize the behaviour of the template that hera generates when a python callable is
    passed to the Script class.

    In order to use your custom ScriptConstructor implementation, you can set it as the Script.constructor field.
    """

    @abstractmethod
    def generate_source(self, instance: "Script") -> str:
        """A function that can inspect the Script instance and generate the source field."""
        raise NotImplementedError

    def transform_values(self, cls: Type["Script"], values: Any) -> Any:
        """A function that will be invoked by the root validator of the Script class."""
        return values

    def transform_script_template_post_build(
        self, instance: "Script", script: _ModelScriptTemplate
    ) -> _ModelScriptTemplate:
        """A hook to transform the generated script template."""
        return script

    def transform_template_post_build(self, instance: "Script", template: _ModelTemplate) -> _ModelTemplate:
        """A hook to transform the generated template."""
        return template


class Script(
    EnvIOMixin,
    CallableTemplateMixin,
    ContainerMixin,
    TemplateMixin,
    ResourceMixin,
    VolumeMountMixin,
):
    """A Script in Argo Workflows acts as a wrapper around a Container, where you can specify Python code to run through `source`.

    In Hera, you should aim to use the script decorator, rather than the Script class directly.
    You will need to refer to the Script class for the kwargs that the decorator can take, but your IDE should give you code completion and type hints.
    """

    container_name: Optional[str] = None
    args: Optional[List[str]] = None
    command: Optional[List[str]] = None
    lifecycle: Optional[Lifecycle] = None
    security_context: Optional[SecurityContext] = None
    source: Optional[Union[Callable, str]] = None
    working_dir: Optional[str] = None
    add_cwd_to_sys_path: Optional[bool] = None
    constructor: Optional[Union[str, ScriptConstructor]] = None

    @validator("constructor", always=True)
    @classmethod
    def _set_constructor(cls, v):
        if v is None:
            # TODO: In the future we can insert
            # detection code here to determine
            # the best constructor to use.
            v = InlineScriptConstructor()
        if isinstance(v, ScriptConstructor):
            return v
        assert isinstance(v, str)
        if v.lower() == "inline":
            return InlineScriptConstructor()
        elif v.lower() == "runner":
            return RunnerScriptConstructor()
        raise ValueError(f"Unknown constructor {v}")

    @validator("command", always=True)
    @classmethod
    def _set_command(cls, v):
        return v or global_config.script_command

    @validator("add_cwd_to_sys_path", always=True)
    @classmethod
    def _set_add_cwd_to_sys_path(cls, v):
        if v is None:
            return True

    @root_validator
    @classmethod
    def _constructor_validate(cls, values):
        constructor = values.get("constructor")
        assert isinstance(constructor, ScriptConstructor)
        return constructor.transform_values(cls, values)

    def _build_template(self) -> _ModelTemplate:
        assert isinstance(self.constructor, ScriptConstructor)

        return self.constructor.transform_template_post_build(
            self,
            _ModelTemplate(
                active_deadline_seconds=self.active_deadline_seconds,
                affinity=self.affinity,
                archive_location=self.archive_location,
                automount_service_account_token=self.automount_service_account_token,
                daemon=self.daemon,
                executor=self.executor,
                fail_fast=self.fail_fast,
                host_aliases=self.host_aliases,
                init_containers=self._build_init_containers(),
                inputs=self._build_inputs(),
                memoize=self.memoize,
                metadata=self._build_metadata(),
                metrics=self._build_metrics(),
                name=self.name,
                node_selector=self.node_selector,
                outputs=self._build_outputs(),
                parallelism=self.parallelism,
                plugin=self.plugin,
                pod_spec_patch=self.pod_spec_patch,
                priority_class_name=self.priority_class_name,
                retry_strategy=self._build_retry_strategy(),
                scheduler_name=self.scheduler_name,
                script=self._build_script(),
                security_context=self.pod_security_context,
                service_account_name=self.service_account_name,
                sidecars=self._build_sidecars(),
                synchronization=self.synchronization,
                timeout=self.timeout,
                tolerations=self.tolerations,
                volumes=self._build_volumes(),
            ),
        )

    def _build_script(self) -> _ModelScriptTemplate:
        assert isinstance(self.constructor, ScriptConstructor)
        if _output_annotations_used(cast(Callable, self.source)) and isinstance(
            self.constructor, RunnerScriptConstructor
        ):
            if not self.constructor.outputs_directory:
                self.constructor.outputs_directory = self.constructor.DEFAULT_HERA_OUTPUTS_DIRECTORY
            if self.constructor.volume_for_outputs is not None:
                if self.constructor.volume_for_outputs.mount_path is None:
                    self.constructor.volume_for_outputs.mount_path = self.constructor.outputs_directory
                self._create_hera_outputs_volume(self.constructor.volume_for_outputs)
        assert self.image
        return self.constructor.transform_script_template_post_build(
            self,
            _ModelScriptTemplate(
                args=self.args,
                command=self.command,
                env=self._build_env(),
                env_from=self._build_env_from(),
                image=self.image,
                # `image_pull_policy` in script wants a string not an `ImagePullPolicy` object
                image_pull_policy=self._build_image_pull_policy(),
                lifecycle=self.lifecycle,
                liveness_probe=self.liveness_probe,
                name=self.container_name,
                ports=self.ports,
                readiness_probe=self.readiness_probe,
                resize_policy=self.resize_policy,
                resources=self._build_resources(),
                restart_policy=self.restart_policy,
                security_context=self.security_context,
                source=self.constructor.generate_source(self),
                startup_probe=self.startup_probe,
                stdin=self.stdin,
                stdin_once=self.stdin_once,
                termination_message_path=self.termination_message_path,
                termination_message_policy=self.termination_message_policy,
                tty=self.tty,
                volume_devices=self.volume_devices,
                volume_mounts=self._build_volume_mounts(),
                working_dir=self.working_dir,
            ),
        )

    def _build_inputs(self) -> Optional[ModelInputs]:
        inputs = super()._build_inputs()
        func_parameters: List[Parameter] = []
        func_artifacts: List[Artifact] = []
        if callable(self.source):
            func_parameters, func_artifacts = _get_inputs_from_callable(self.source)

        return cast(Optional[ModelInputs], self._aggregate_callable_io(inputs, func_parameters, func_artifacts, False))

    def _build_outputs(self) -> Optional[ModelOutputs]:
        outputs = super()._build_outputs()

        if not callable(self.source):
            return outputs

        outputs_directory = None
        if isinstance(self.constructor, RunnerScriptConstructor):
            outputs_directory = self.constructor.outputs_directory or self.constructor.DEFAULT_HERA_OUTPUTS_DIRECTORY

        out_parameters, out_artifacts = _get_outputs_from_return_annotation(self.source, outputs_directory)
        func_parameters, func_artifacts = _get_outputs_from_parameter_annotations(self.source, outputs_directory)
        func_parameters.extend(out_parameters)
        func_artifacts.extend(out_artifacts)

        return cast(
            Optional[ModelOutputs], self._aggregate_callable_io(outputs, func_parameters, func_artifacts, True)
        )

    def _aggregate_callable_io(
        self,
        current_io: Optional[Union[ModelInputs, ModelOutputs]],
        func_parameters: List[Parameter],
        func_artifacts: List[Artifact],
        output: bool,
    ) -> Union[ModelOutputs, ModelInputs, None]:
        """Aggregate the Inputs/Outputs with parameters and artifacts extracted from a callable."""
        if not func_parameters and not func_artifacts:
            return current_io
        if current_io is None:
            if output:
                return ModelOutputs(
                    parameters=[p.as_output() for p in func_parameters] or None,
                    artifacts=[a._build_artifact() for a in func_artifacts] or None,
                )

            return ModelInputs(
                parameters=[p.as_input() for p in func_parameters] or None,
                artifacts=[a._build_artifact() for a in func_artifacts] or None,
            )

        seen_params = {p.name for p in current_io.parameters or []}
        seen_artifacts = {a.name for a in current_io.artifacts or []}

        for param in func_parameters:
            if param.name not in seen_params and param.name not in seen_artifacts:
                if current_io.parameters is None:
                    current_io.parameters = []
                if output:
                    current_io.parameters.append(param.as_output())
                else:
                    current_io.parameters.append(param.as_input())

        for artifact in func_artifacts:
            if artifact.name not in seen_artifacts:
                if current_io.artifacts is None:
                    current_io.artifacts = []
                current_io.artifacts.append(artifact._build_artifact())

        return current_io

    def _create_hera_outputs_volume(self, volume: _BaseVolume) -> None:
        """Add given volume to the script template for the automatic saving of the hera outputs."""
        assert isinstance(self.constructor, RunnerScriptConstructor)

        if self.volumes is None:
            self.volumes = []
        elif isinstance(self.volumes, Sequence):
            self.volumes = list(self.volumes)
        elif not isinstance(self.volumes, list):
            self.volumes = [self.volumes]

        if volume not in self.volumes:
            self.volumes.append(volume)


def _get_outputs_from_return_annotation(
    source: Callable,
    outputs_directory: Optional[str],
) -> Tuple[List[Parameter], List[Artifact]]:
    """Returns a tuple of output Parameters and Artifacts defined in the function signature's return annotation."""
    parameters = []
    artifacts = []

    def append_annotation(annotation: Union[Artifact, Parameter]):
        if isinstance(annotation, Artifact):
            if annotation.path is None and outputs_directory is not None:
                annotation.path = outputs_directory + f"/artifacts/{annotation.name}"
            artifacts.append(annotation)
        elif isinstance(annotation, Parameter):
            if annotation.value_from is None and outputs_directory is not None:
                annotation.value_from = ValueFrom(path=outputs_directory + f"/parameters/{annotation.name}")
            parameters.append(annotation)

    return_annotation = inspect.signature(source).return_annotation
    if param_or_artifact := get_workflow_annotation(return_annotation):
        append_annotation(param_or_artifact)
    elif get_origin(return_annotation) is tuple:
        for annotation in get_args(return_annotation):
            if isinstance(annotation, type) and issubclass(annotation, (OutputV1, OutputV2)):
                raise ValueError("Output cannot be part of a tuple output")

            if param_or_artifact := get_workflow_annotation(annotation):
                append_annotation(param_or_artifact)
    elif isinstance(return_annotation, type) and issubclass(return_annotation, (OutputV1, OutputV2)):
        if not _flag_enabled(_SCRIPT_PYDANTIC_IO_FLAG):
            raise ValueError(
                (
                    "Unable to instantiate {} since it is an experimental feature."
                    " Please turn on experimental features by setting "
                    '`hera.shared.global_config.experimental_features["{}"] = True`.'
                    " Note that experimental features are unstable and subject to breaking changes."
                ).format(return_annotation, _SCRIPT_PYDANTIC_IO_FLAG)
            )

        output_class = return_annotation
        for output in output_class._get_outputs():
            append_annotation(output)

    return parameters, artifacts


def _get_outputs_from_parameter_annotations(
    source: Callable,
    outputs_directory: Optional[str],
) -> Tuple[List[Parameter], List[Artifact]]:
    """Returns a tuple of output Parameters and Artifacts defined in the function signature parameters."""
    parameters: List[Parameter] = []
    artifacts: List[Artifact] = []

    for name, p in inspect.signature(source).parameters.items():
        annotation = construct_io_from_annotation(name, p.annotation)
        if not annotation.output:
            continue

        if isinstance(annotation, Parameter) and annotation.value_from is None and outputs_directory is not None:
            annotation.value_from = ValueFrom(path=outputs_directory + f"/parameters/{annotation.name}")
        elif isinstance(annotation, Artifact) and annotation.path is None and outputs_directory is not None:
            annotation.path = outputs_directory + f"/artifacts/{annotation.name}"

        if isinstance(annotation, Artifact):
            artifacts.append(annotation)
        elif isinstance(annotation, Parameter):
            parameters.append(annotation)

    return parameters, artifacts


def _get_inputs_from_callable(source: Callable) -> Tuple[List[Parameter], List[Artifact]]:
    """Return all inputs from the function.

    This includes all basic Python function parameters, and all parameters with a Parameter or Artifact annotation.
    For the Pydantic IO experimental feature, any input parameter which is a subclass of Input, the fields of the
    class will be used as inputs, rather than the class itself.

    Note, the given Parameter/Artifact names in annotations of different inputs could clash, which will raise a ValueError.
    """
    parameters = []
    artifacts = []

    for func_param in inspect.signature(source).parameters.values():
        # If the annotation is not subscripted, then we can directly check if it is an Input type annotation.
        # Otherwise, we check if it is of the form `Annotated[...]`, and subsequently check whether the unwrapped
        # annotation is a class which we can then check if it is a subclass. Otherwise, an annotation of the form
        # `Annotated[Literal[...]]` will raise an exception as `typing.Literal` is not a class (but an object).
        if (
            not is_subscripted(func_param.annotation)
            and issubclass(func_param.annotation, (InputV1, InputV2))
            or is_annotated(func_param.annotation)
            and inspect.isclass(unwrap_annotation(func_param.annotation))
            and issubclass(unwrap_annotation(func_param.annotation), (InputV1, InputV2))
        ):
            if not _flag_enabled(_SCRIPT_PYDANTIC_IO_FLAG):
                raise ValueError(
                    (
                        "Unable to instantiate {} since it is an experimental feature."
                        " Please turn on experimental features by setting "
                        '`hera.shared.global_config.experimental_features["{}"] = True`.'
                        " Note that experimental features are unstable and subject to breaking changes."
                    ).format(func_param.annotation, _SCRIPT_PYDANTIC_IO_FLAG)
                )

            if len(inspect.signature(source).parameters) != 1:
                raise SyntaxError("Only one function parameter can be specified when using an Input.")

            input_class = func_param.annotation
            if (
                func_param.default != inspect.Parameter.empty
                and func_param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
            ):
                object_override = func_param.default
                parameters.extend(input_class._get_parameters(object_override=object_override))
            else:
                parameters.extend(input_class._get_parameters())

            artifacts.extend(input_class._get_artifacts(add_missing_path=True))

        else:
            io = construct_io_from_annotation(func_param.name, func_param.annotation)
            if io.output:
                continue

            if isinstance(io, Artifact):
                if io.path is None:
                    io.path = io._get_default_inputs_path()

                artifacts.append(io)
            elif isinstance(io, Parameter):
                if io.default is not None:
                    raise ValueError(
                        "default cannot be set via the Parameter's default, use a Python default value instead."
                    )
                if func_param.default != inspect.Parameter.empty:
                    io.default = serialize(func_param.default)

                if origin_type_issupertype(func_param.annotation, NoneType) and io.default != "null":
                    raise ValueError(f"Optional parameter '{func_param.name}' must have a default value of None.")
                parameters.append(io)

    return parameters, artifacts


def _extract_return_annotation_output(source: Callable) -> List:
    """Extract the output annotations from the return annotation of the function signature."""
    output: List[Union[Tuple[type, Union[Parameter, Artifact]], Type[Union[OutputV1, OutputV2]]]] = []

    return_annotation = inspect.signature(source).return_annotation
    origin_type = get_origin(return_annotation)
    annotation_args = get_args(return_annotation)
    if get_workflow_annotation(return_annotation):
        output.append(annotation_args)
    elif origin_type is tuple:
        workflow_args = [
            get_args(annotated_type) for annotated_type in annotation_args if get_workflow_annotation(annotated_type)
        ]

        # If all tuple elements are annotated as Parameter/Artifact
        if len(workflow_args) == len(annotation_args):
            output.extend(workflow_args)
        # Only some tuple elements are annotated as Parameter/Artifact
        elif workflow_args:
            raise ValueError(
                f"Function '{source.__name__}' output has partially annotated tuple return type. "
                "Tuple elements must be all Annotated as Parameter/Artifact, or contain no Parameter/Artifact annotations for a raw tuple return type."
            )
    elif (
        origin_type is None
        and isinstance(return_annotation, type)
        and issubclass(return_annotation, (OutputV1, OutputV2))
    ):
        output.append(return_annotation)

    return output


def _extract_all_output_annotations(source: Callable) -> List:
    """Extract the output annotations out of the function signature.

    This includes parameters marked as outputs and the return annotation of `source`.
    """
    output = []

    for _, func_param in inspect.signature(source).parameters.items():
        io = construct_io_from_annotation(func_param.name, func_param.annotation)
        if io.output:
            output.append(io)

    output.extend(_extract_return_annotation_output(source))

    return output


def _output_annotations_used(source: Callable) -> bool:
    """Check if any output annotations are used.

    This includes parameters marked as outputs and the return annotation of `source`.
    """
    if not callable(source):
        return False

    return bool(_extract_all_output_annotations(source))


FuncIns = ParamSpec("FuncIns")  # For input types of given func to script decorator
FuncR = TypeVar("FuncR")  # For return type of given func to script decorator
FuncRCov = TypeVar("FuncRCov", covariant=True)

ScriptIns = ParamSpec("ScriptIns")  # For input attributes of Script class


class _ScriptDecoratedFunction(Generic[FuncIns, FuncRCov], Protocol):
    """Type assigned to functions decorated with @script."""

    # Note: For more details about overload-overlap, see https://github.com/python/typeshed/issues/12178

    @overload
    def __call__(  # type: ignore [overload-overlap]
        self, *args: FuncIns.args, **kwargs: FuncIns.kwargs
    ) -> FuncRCov:
        # Note: this overload is for calling the decorated function.
        # No docstring is provided, so VS Code will use the docstring of the decorated function.
        ...

    @overload
    def __call__(  # type: ignore [overload-overlap, misc]
        self,
    ) -> Optional[Union[Step, Task]]:
        """Create a Step or Task or add the script as a template to the workflow, depending on the context.

        * Under a DAG context, creates and returns a Task.
        * Under a Steps or Parallel context, creates and returns a Step.
        * Under a Workflow context, adds the script as a template to the Workflow and returns None.

        Use `assert isinstance(result, Step)` or `assert isinstance(result, Task)` to select
        the correct type if using a type-checker.
        """

    @overload
    def __call__(  # type: ignore [overload-overlap]
        self,
        *,
        name: str = ...,
        continue_on: Optional[ContinueOn] = ...,
        hooks: Optional[Dict[str, LifecycleHook]] = ...,
        on_exit: Optional[Union[str, Templatable]] = ...,
        template: Optional[Union[str, _ModelTemplate, Templatable]] = ...,
        template_ref: Optional[TemplateRef] = ...,
        inline: Optional[Union[_ModelTemplate, Templatable]] = ...,
        when: Optional[str] = ...,
        with_sequence: Optional[_ModelSequence] = ...,
        arguments: ArgumentsT = ...,
        with_param: Optional[Any] = ...,
        with_items: Optional[OneOrMany[Any]] = ...,
    ) -> Union[Step, Task]:
        """Create a Step or Task, depending on context.

        * Under a DAG context, creates and returns a Task.
        * Under a Steps or Parallel context, creates and returns a Step.

        Use `assert isinstance(result, Step)` or `assert isinstance(result, Task)` to select
        the correct type if using a type-checker.
        """
        # Note: signature must match the Step constructor, except that while name is required for Step,
        # it is automatically inferred from the name of the decorated function when invoked.

    @overload
    def __call__(  # type: ignore [overload-overlap]
        self,
        *,
        name: str = ...,
        continue_on: Optional[ContinueOn] = ...,
        hooks: Optional[Dict[str, LifecycleHook]] = ...,
        on_exit: Optional[Union[str, Templatable]] = ...,
        template: Optional[Union[str, _ModelTemplate, Templatable]] = ...,
        template_ref: Optional[TemplateRef] = ...,
        inline: Optional[Union[_ModelTemplate, Templatable]] = ...,
        when: Optional[str] = ...,
        with_sequence: Optional[_ModelSequence] = ...,
        arguments: ArgumentsT = ...,
        with_param: Optional[Any] = ...,
        with_items: Optional[OneOrMany[Any]] = ...,
        dependencies: Optional[List[str]] = ...,
        depends: Optional[str] = ...,
    ) -> Task:
        """Create and return a Task.

        Must be invoked under a DAG context.
        """
        # Note: signature must match the Task constructor, except that while name is required for Task,
        # it is automatically inferred from the name of the decorated function when invoked.


# Pass actual class of Script to bind inputs to the ParamSpec above
def _add_type_hints(
    _script: Callable[ScriptIns, Script],
) -> Callable[
    ...,
    Callable[
        ScriptIns,  # this adds Script type hints to the underlying *library* function kwargs, i.e. `script`
        Callable[  # we will return a function that is a decorator
            [Callable[FuncIns, FuncR]],  # taking underlying *user* function
            _ScriptDecoratedFunction[  # and returning an overloaded method that can additionally return Task or Step
                FuncIns, FuncR
            ],
        ],
    ],
]:
    """Adds type hints to the decorated function."""
    return lambda func: func


@_add_type_hints(Script)
def script(**script_kwargs) -> Callable:
    """A decorator that wraps a function into a Script object.

    Using this decorator users can define a function that will be executed as a script in a container. Once the
    `Script` is returned users can use it as they generally use a `Script` e.g. as a callable inside a DAG or Steps.
    Note that invoking the function will result in the template associated with the script to be added to the
    workflow context, so users do not have to worry about that.

    Args:
        **script_kwargs: Keyword arguments to be passed to the Script object.

    Returns:
        Function that wraps a given function into a `Script`.
    """

    def script_wrapper(func: Callable[FuncIns, FuncR]) -> Callable:
        """Wraps the given callable so it can be invoked as a Step or Task.

        Parameters
        ----------
        func: Callable
            Function to wrap.

        Returns:
        -------
        Callable
            Callable that represents the `Script` object `__call__` method when in a Steps or DAG context,
            otherwise returns the callable function unchanged.
        """
        # instance methods are wrapped in `staticmethod`. Hera can capture that type and extract the underlying
        # function for remote submission since it does not depend on any class or instance attributes, so it is
        # submittable
        if isinstance(func, staticmethod):
            source: Callable = func.__func__
        else:
            source = func

        if "name" in script_kwargs:
            # take the client-provided `name` if it is submitted, pop the name for otherwise there will be two
            # kwargs called `name`
            name = script_kwargs.pop("name")
        else:
            # otherwise populate the `name` from the function name
            name = source.__name__.replace("_", "-")

        s = Script(name=name, source=source, **script_kwargs)

        @wraps(func)
        def task_wrapper(*args, **kwargs) -> Union[FuncR, Step, Task, None]:
            """Invokes a `Script` object's `__call__` method using the given SubNode (Step or Task) args/kwargs."""
            if _context.active:
                return s.__call__(*args, **kwargs)
            return func(*args, **kwargs)

        # Set the wrapped function to the original function so that we can use it later
        task_wrapper.wrapped_function = func  # type: ignore
        return task_wrapper

    return script_wrapper


class InlineScriptConstructor(ScriptConstructor):
    """`InlineScriptConstructor` is a script constructor that submits a script as a `source` to Argo.

    This script constructor is focused on taking a Python script/function "as is" for remote execution. The
    constructor processes the script to infer what parameters it needs to deserialize so the script can execute.
    The submitted script will contain prefixes such as new imports, e.g. `import os`, `import json`, etc. and
    will contain the necessary `json.loads` calls to deserialize the parameters so they are usable by the script just
    like a normal Python script/function.
    """

    add_cwd_to_sys_path: Optional[bool] = None

    @staticmethod
    def _roundtrip(source):
        tree = ast.parse(source)
        if hasattr(ast, "unparse"):
            return ast.unparse(tree)
        return ast.unparse(tree)

    def _get_param_script_portion(self, instance: Script) -> str:
        """Constructs and returns a script that loads the parameters of the specified arguments.

        Since Argo passes parameters through `{{input.parameters.name}}` it can be very cumbersome for users to
        manage that. This creates a script that automatically imports json and loads/adds code to interpret
        each independent argument into the script.

        Returns:
        -------
        str
            The string representation of the script to load.
        """
        inputs = instance._build_inputs()
        assert inputs
        extract = "import json\n"
        for param in sorted(inputs.parameters or [], key=lambda x: x.name):
            # Hera does not know what the content of the `InputFrom` is, coming from another task. In some cases
            # non-JSON encoded strings are returned, which fail the loads, but they can be used as plain strings
            # which is why this captures that in an except. This is only used for `InputFrom` cases as the extra
            # payload of the script is not necessary when regular input is set on the task via `func_params`
            if param.value_from is None:
                extract += f"""try: {param.name} = json.loads(r'''{{{{inputs.parameters.{param.name}}}}}''')\n"""
                extract += f"""except: {param.name} = r'''{{{{inputs.parameters.{param.name}}}}}'''\n"""
        return textwrap.dedent(extract) if extract != "import json\n" else ""

    def generate_source(self, instance: Script) -> str:
        """Assembles and returns a script representation of the given function.

        This also assembles any extra script material prefixed to the string source.
        The script is expected to be a callable function the client is interested in submitting
        for execution on Argo and the `script_extra` material represents the parameter loading part obtained, likely,
        through `get_param_script_portion`.

        Returns:
        -------
        str
            Final formatted script.
        """
        if not callable(instance.source):
            assert isinstance(instance.source, str)
            return instance.source
        args = inspect.getfullargspec(instance.source).args
        script = ""
        # Argo will save the script as a file and run it with cmd:
        # - python /argo/staging/script
        # However, this prevents the script from importing modules in its cwd,
        # since it's looking for files relative to the script path.
        # We fix this by appending the cwd path to sys:
        if instance.add_cwd_to_sys_path or self.add_cwd_to_sys_path:
            script = "import os\nimport sys\nsys.path.append(os.getcwd())\n"

        script_extra = self._get_param_script_portion(instance) if args else None
        if script_extra:
            script += copy.deepcopy(script_extra)
            script += "\n"

        # We use ast parse/unparse to get the source code of the function
        # in order to have consistent looking functions and getting rid of any comments
        # parsing issues.
        # See https://github.com/argoproj-labs/hera/issues/572
        content = self._roundtrip(textwrap.dedent(inspect.getsource(instance.source))).splitlines()
        for i, line in enumerate(content):
            if line.startswith("def") or line.startswith("async def"):
                break

        s = "\n".join(content[i + 1 :])
        script += textwrap.dedent(s)
        return textwrap.dedent(script)


class RunnerScriptConstructor(ScriptConstructor):
    """`RunnerScriptConstructor` is a script constructor that runs a script in a container.

    The runner script, also known as "The Hera runner", takes a script/Python function definition, infers the path
    to the function (module import), assembles a path to invoke the function, and passes any specified parameters
    to the function. This helps users "save" on the `source` space required for submitting a function for remote
    execution on Argo. Execution within the container *requires* the executing container to include the file that
    contains the submitted script. More specifically, the container must be created in some process (e.g. CI), so that
    it conains the script to run remotely.
    """

    outputs_directory: Optional[str] = None
    """Used for saving outputs when defined using annotations."""

    volume_for_outputs: Optional[_BaseVolume] = None
    """Volume to use if saving outputs when defined using annotations."""

    DEFAULT_HERA_OUTPUTS_DIRECTORY: str = "/tmp/hera-outputs"
    """Used as the default value for when the outputs_directory is not set"""

    pydantic_mode: Optional[Literal[1, 2]] = None
    """Used for selecting the pydantic version used for BaseModels.
    Allows for using pydantic.v1 BaseModels with pydantic v2.
    Defaults to the installed version of Pydantic."""

    @validator("pydantic_mode", always=True)
    def _pydantic_mode(cls, value: Optional[Literal[1, 2]]) -> Optional[Literal[1, 2]]:
        if value and value > _PYDANTIC_VERSION:
            raise ValueError("v2 pydantic mode only available for pydantic>=2")
        return value

    def transform_values(self, cls: Type[Script], values: Any) -> Any:
        """A function that can inspect the Script instance and generate the source field."""
        if not callable(values.get("source")):
            return values

        if values.get("args") is not None:
            raise ValueError("Cannot specify args when callable is True")

        module = values["source"].__module__

        if module == "__main__":
            from hera.workflows._runner.util import create_module_string

            module = create_module_string(Path(values["source"].__globals__["__file__"]))

        values["args"] = [
            "-m",
            "hera.workflows.runner",
            "-e",
            f"{module}:{values['source'].__name__}",
        ]

        return values

    def generate_source(self, instance: Script) -> str:
        """A function that can inspect the Script instance and generate the source field."""
        return f"{g.inputs.parameters:$}"

    def transform_script_template_post_build(
        self, instance: "Script", script: _ModelScriptTemplate
    ) -> _ModelScriptTemplate:
        """A hook to transform the generated script template."""
        script_env = []

        if self.outputs_directory:
            script_env.append(EnvVar(name="hera__outputs_directory", value=self.outputs_directory))
        if self.pydantic_mode:
            script_env.append(EnvVar(name="hera__pydantic_mode", value=str(self.pydantic_mode)))
        if _flag_enabled(_SCRIPT_PYDANTIC_IO_FLAG):
            script_env.append(EnvVar(name="hera__script_pydantic_io", value=""))

        if script_env:
            if not script.env:
                # If user did not set any env vars themselves then we need to initialise the list
                script.env = []

            script.env.extend(script_env)

        return script


__all__ = ["Script", "script", "ScriptConstructor", "InlineScriptConstructor", "RunnerScriptConstructor"]
