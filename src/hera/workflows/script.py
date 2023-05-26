"""The script module provides the Script class.

See https://argoproj.github.io/argo-workflows/workflow-concepts/#script
for more on scripts.
"""

import copy
import inspect
import textwrap
from abc import abstractmethod
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    overload,
)

from pydantic import root_validator, validator
from typing_extensions import ParamSpec

from hera.expr import g
from hera.shared import BaseMixin, global_config
from hera.workflows._context import _context
from hera.workflows._mixins import (
    CallableTemplateMixin,
    ContainerMixin,
    EnvIOMixin,
    ExperimentalMixin,
    ResourceMixin,
    TemplateMixin,
    VolumeMountMixin,
)
from hera.workflows._unparse import roundtrip
from hera.workflows.models import (
    Inputs as ModelInputs,
    Lifecycle,
    ScriptTemplate as _ModelScriptTemplate,
    SecurityContext,
    Template as _ModelTemplate,
)
from hera.workflows.parameter import MISSING, Parameter
from hera.workflows.steps import Step
from hera.workflows.task import Task


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
        """A function that will be inokved by the root validator of the Script class."""
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
    """A Script acts as a wrapper around a container. In Hera this defaults to a "python:3.8" image
    specified by global_config.image, which runs a python source specified by `Script.source`.
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

    def _build_inputs(self) -> Optional[ModelInputs]:
        inputs = super()._build_inputs()
        func_parameters = _get_parameters_from_callable(self.source) if callable(self.source) else None

        if inputs is None and func_parameters is None:
            return None
        elif func_parameters is None:
            return inputs
        elif inputs is None:
            inputs = ModelInputs(parameters=func_parameters)

        already_set_params = {p.name for p in inputs.parameters or []}
        already_set_artifacts = {p.name for p in inputs.artifacts or []}
        for param in func_parameters:
            if param.name not in already_set_params and param.name not in already_set_artifacts:
                inputs.parameters = [param] if inputs.parameters is None else inputs.parameters + [param]
        return inputs

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
                init_containers=self.init_containers,
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
                priority=self.priority,
                priority_class_name=self.priority_class_name,
                retry_strategy=self.retry_strategy,
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
        return self.constructor.transform_script_template_post_build(
            self,
            _ModelScriptTemplate(
                args=self.args,
                command=self.command,
                env=self._build_env(),
                env_from=self._build_env_from(),
                image=self.image,
                image_pull_policy=self._build_image_pull_policy(),
                lifecycle=self.lifecycle,
                liveness_probe=self.liveness_probe,
                name=self.container_name,
                ports=self.ports,
                readiness_probe=self.readiness_probe,
                resources=self._build_resources(),
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


def _get_parameters_from_callable(source: Callable) -> Optional[List[Parameter]]:
    # If there are any kwargs arguments associated with the function signature,
    # we store these as we can set them as default values for argo arguments
    source_signature: Dict[str, Optional[object]] = {}
    for p in inspect.signature(source).parameters.values():
        if p.default != inspect.Parameter.empty and p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            source_signature[p.name] = p.default
        else:
            source_signature[p.name] = MISSING

    if len(source_signature) == 0:
        return None
    return [Parameter(name=n, default=v) for n, v in source_signature.items()]


FuncIns = ParamSpec("FuncIns")  # For input types of given func to script decorator
FuncR = TypeVar("FuncR")  # For return type of given func to script decorator
ScriptIns = ParamSpec("ScriptIns")  # For attribute types of Script


def _take_annotation_from(
    _: Callable[
        ScriptIns,
        Callable[[Callable[FuncIns, FuncR]], Union[Callable[FuncIns, FuncR], Callable[ScriptIns, Union[Task, Step]]]],
    ]
) -> Callable[
    [Callable],
    Callable[
        ScriptIns,
        Callable[[Callable[FuncIns, FuncR]], Union[Callable[FuncIns, FuncR], Callable[ScriptIns, Union[Task, Step]]]],
    ],
]:
    def decorator(
        real_function: Callable,
    ) -> Callable[
        ScriptIns,
        Callable[[Callable[FuncIns, FuncR]], Union[Callable[FuncIns, FuncR], Callable[ScriptIns, Union[Task, Step]]]],
    ]:
        def new_function(
            *args: ScriptIns.args, **kwargs: ScriptIns.kwargs
        ) -> Callable[
            [Callable[FuncIns, FuncR]], Union[Callable[FuncIns, FuncR], Callable[ScriptIns, Union[Task, Step]]]
        ]:
            return real_function(*args, **kwargs)

        return new_function

    return decorator


@_take_annotation_from(Script)  # type: ignore
def script(**script_kwargs):
    """A decorator that wraps a function into a Script object.

    Using this decorator users can define a function that will be executed as a script in a container. Once the
    `Script` is returned users can use it as they generally use a `Script` e.g. as a callable inside a DAG or Steps.
    Note that invoking the function will result in the template associated with the script to be added to the
    workflow context, so users do not have to worry about that.

    Parameters
    ----------
    **script_kwargs
        Keyword arguments to be passed to the Script object.

    Returns
    -------
    Callable
        Function that wraps a given function into a `Script`.
    """

    def script_wrapper(
        func: Callable[FuncIns, FuncR],
    ) -> Union[Callable[FuncIns, FuncR], Callable[ScriptIns, Union[Task, Step]]]:
        """Wraps the given callable into a `Script` object that can be invoked.

        Parameters
        ----------
        func: Callable
            Function to wrap.

        Returns
        -------
        Callable
            Another callable that represents the `Script` object `__call__` method when in a Steps or DAG context,
            otherwise return the callable function unchanged.
        """
        s = Script(name=func.__name__.replace("_", "-"), source=func, **script_kwargs)

        @overload
        def task_wrapper(*args: FuncIns.args, **kwargs: FuncIns.kwargs) -> FuncR:
            ...

        @overload
        def task_wrapper(*args: ScriptIns.args, **kwargs: ScriptIns.kwargs) -> Union[Step, Task]:
            ...

        @wraps(func)
        def task_wrapper(*args, **kwargs):
            """Invokes a `Script` object's `__call__` method using the given `task_params`"""
            if _context.active:
                return s.__call__(*args, **kwargs)
            return func(*args, **kwargs)

        # Set the wrapped function to the original function so that we can use it later
        task_wrapper.wrapped_function = func  # type: ignore
        return task_wrapper

    return script_wrapper


class InlineScriptConstructor(ScriptConstructor):
    add_cwd_to_sys_path: Optional[bool] = None

    def _get_param_script_portion(self, instance: Script) -> str:
        """Constructs and returns a script that loads the parameters of the specified arguments. Since Argo passes
        parameters through {{input.parameters.name}} it can be very cumbersome for users to manage that. This creates a
        script that automatically imports json and loads/adds code to interpret each independent argument into the
        script.

        Returns
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
            extract += f"""try: {param.name} = json.loads(r'''{{{{inputs.parameters.{param.name}}}}}''')\n"""
            extract += f"""except: {param.name} = r'''{{{{inputs.parameters.{param.name}}}}}'''\n"""
        return textwrap.dedent(extract)

    def generate_source(self, instance: Script) -> str:
        """Assembles and returns a script representation of the given function, along with the extra script material
        prefixed to the string. The script is expected to be a callable function the client is interested in submitting
        for execution on Argo and the script_extra material represents the parameter loading part obtained, likely,
        through get_param_script_portion.

        Returns
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
        content = roundtrip(inspect.getsource(instance.source)).splitlines()
        for i, line in enumerate(content):
            if line.startswith("def") or line.startswith("async def"):
                break

        s = "\n".join(content[i + 1 :])
        script += textwrap.dedent(s)
        return textwrap.dedent(script)


class RunnerScriptConstructor(ScriptConstructor, ExperimentalMixin):
    _flag: str = "script_runner"

    def transform_values(self, cls: Type[Script], values: Any) -> Any:
        if not callable(values.get("source")):
            return values

        if values.get("args") is not None:
            raise ValueError("Cannot specify args when callable is True")
        values["args"] = [
            "-m",
            "hera.workflows.runner",
            "-e",
            f'{values["source"].__module__}:{values["source"].__name__}',
        ]

        return values

    def generate_source(self, instance: Script) -> str:
        return f"{g.inputs.parameters:$}"


__all__ = ["Script", "script", "ScriptConstructor", "InlineScriptConstructor", "RunnerScriptConstructor"]
