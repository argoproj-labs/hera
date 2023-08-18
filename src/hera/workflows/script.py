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
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

from pydantic import root_validator, validator
from typing_extensions import ParamSpec, get_args, get_origin

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
from hera.workflows.artifact import (
    Artifact,
)
from hera.workflows.models import (
    EnvVar,
    Inputs as ModelInputs,
    Lifecycle,
    Outputs as ModelOutputs,
    ScriptTemplate as _ModelScriptTemplate,
    SecurityContext,
    Template as _ModelTemplate,
)
from hera.workflows.parameter import MISSING, Parameter
from hera.workflows.protocol import Inputable
from hera.workflows.steps import Step
from hera.workflows.task import Task
from hera.workflows.volume import EmptyDirVolume

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore


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
    """A Script acts as a wrapper around a container.

    In Hera this defaults to a "python:3.8" image specified by global_config.image, which runs a python source
    specified by `Script.source`.
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
        hera_outputs_used = self._check_hera_outputs_used()
        if hera_outputs_used:
            self._create_new_volume()
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
                script=self._build_script(hera_outputs_used),
                security_context=self.pod_security_context,
                service_account_name=self.service_account_name,
                sidecars=self._build_sidecars(),
                synchronization=self.synchronization,
                timeout=self.timeout,
                tolerations=self.tolerations,
                volumes=self._build_volumes(),
            ),
        )

    def _build_script(self, hera_outputs_used: bool = False) -> _ModelScriptTemplate:
        assert isinstance(self.constructor, ScriptConstructor)
        image_pull_policy = self._build_image_pull_policy()

        env = self._build_env()
        if (
            isinstance(self.constructor, RunnerScriptConstructor)
            and global_config.experimental_features["script_annotations"]
        ):
            if not env:
                env = []
            env.append(EnvVar(name="hera__script_annotations", value=""))
            if hera_outputs_used:
                env.append(EnvVar(name="hera__outputs_directory", value=self._get_outputs_directory()))

        return self.constructor.transform_script_template_post_build(
            self,
            _ModelScriptTemplate(
                args=self.args,
                command=self.command,
                env=env,
                env_from=self._build_env_from(),
                image=self.image,
                # `image_pull_policy` in script wants a string not an `ImagePullPolicy` object
                image_pull_policy=None if image_pull_policy is None else image_pull_policy.value,
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

    def _build_inputs(self) -> Optional[ModelInputs]:
        inputs = super()._build_inputs()
        func_parameters: List[Parameter] = []
        func_artifacts: List[Artifact] = []
        if callable(self.source):
            if global_config.experimental_features["script_annotations"]:
                func_parameters, func_artifacts = _get_parameters_and_artifacts_from_callable(self.source)
            else:
                func_parameters = _get_parameters_from_callable(self.source)

        return cast(Optional[ModelInputs], self._process_io(inputs, func_parameters, func_artifacts, False))

    def _build_outputs(self) -> Optional[ModelOutputs]:
        outputs = super()._build_outputs()

        if not callable(self.source):
            return outputs

        if not global_config.experimental_features["script_annotations"]:
            return outputs

        out_parameters, out_artifacts = _get_outputs_from_callable(self.source)
        func_parameters, func_artifacts = _get_outputs_from_callable_signature(self.source)
        func_parameters.extend(out_parameters)
        func_artifacts.extend(out_artifacts)

        return cast(Optional[ModelOutputs], self._process_io(outputs, func_parameters, func_artifacts, True))

    def _process_io(
        self,
        current_io: Optional[Union[ModelInputs, ModelOutputs]],
        func_parameters: List[Parameter],
        func_artifacts: List[Artifact],
        output: bool,
    ) -> Union[ModelOutputs, ModelInputs, None]:
        if current_io is None and not func_parameters and not func_artifacts:
            return None
        if not func_parameters and not func_artifacts:
            return current_io
        if current_io is None:
            if output:
                current_io = ModelOutputs(
                    parameters=[p.as_output() for p in func_parameters] or None,
                    artifacts=[a._build_artifact() for a in func_artifacts] or None,
                )
            else:
                current_io = ModelInputs(
                    parameters=[p.as_input() for p in func_parameters] or None,
                    artifacts=[a._build_artifact() for a in func_artifacts] or None,
                )

        already_set_params = {p.name for p in current_io.parameters or []}
        already_set_artifacts = {a.name for a in current_io.artifacts or []}

        for param in func_parameters:
            if param.name not in already_set_params and param.name not in already_set_artifacts:
                if current_io.parameters is None:
                    current_io.parameters = []
                if output:
                    current_io.parameters.append(param.as_output())
                else:
                    current_io.parameters.append(param.as_input())

        for artifact in func_artifacts:
            if artifact.name not in already_set_params and artifact.name not in already_set_artifacts:
                if current_io.artifacts is None:
                    current_io.artifacts = []
                current_io.artifacts.append(artifact._build_artifact())

        return current_io

    def _check_hera_outputs_used(self) -> bool:
        """Check if hera outputs are used. This is needed to know if we need to create a volume."""
        if not callable(self.source):
            return False
        outputs = extract_output_annotations(cast(Callable, self.source))
        return outputs is not None

    def _create_new_volume(self) -> None:
        """Create the new volume as an EmptyDirVolume if needed."""
        new_volume = EmptyDirVolume(name="hera__outputs_directory", mount_path=self._get_outputs_directory())

        if not isinstance(self.volumes, list) and self.volumes is not None:
            self.volumes = [self.volumes]
        elif self.volumes is None:
            self.volumes = []

        if new_volume not in self.volumes:
            self.volumes.append(new_volume)

    def _get_outputs_directory(self) -> str:
        """Get the outputs directory from the constructor, provide a default if not set."""
        if isinstance(self.constructor, RunnerScriptConstructor):
            if self.constructor.outputs_directory is not None:
                return self.constructor.outputs_directory
        return "/hera/outputs"


def _get_parameters_from_callable(source: Callable) -> List[Parameter]:
    # If there are any kwargs arguments associated with the function signature,
    # we store these as we can set them as default values for argo arguments
    parameters = []

    for p in inspect.signature(source).parameters.values():
        if p.default != inspect.Parameter.empty and p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            default = p.default
        else:
            default = MISSING

        param = Parameter(name=p.name, default=default)
        parameters.append(param)

    return parameters


def _get_outputs_from_callable(
    source: Callable,
) -> Tuple[List[Parameter], List[Artifact]]:
    """Look through the function signature return and find all the output Parameters and Artifacts defined there."""
    parameters = []
    artifacts = []

    if get_origin(inspect.signature(source).return_annotation) is Annotated:
        annotation = get_args(inspect.signature(source).return_annotation)[1]
        if isinstance(annotation, Artifact):
            artifacts.append(annotation)
        elif isinstance(annotation, Parameter):
            parameters.append(annotation)
    elif get_origin(inspect.signature(source).return_annotation) is tuple:
        for a in get_args(inspect.signature(source).return_annotation):
            annotation = get_args(a)[1]
            if isinstance(annotation, Artifact):
                artifacts.append(annotation)
            elif isinstance(annotation, Parameter):
                parameters.append(annotation)

    return parameters, artifacts


def _get_outputs_from_callable_signature(source: Callable) -> Tuple[List[Parameter], List[Artifact]]:
    """Look through the function signature parameters and find all Parameters and Artifacts annotated as output."""
    parameters: List[Parameter] = []
    artifacts: List[Artifact] = []

    for name, p in inspect.signature(source).parameters.items():
        if get_origin(p.annotation) is not Annotated:
            continue
        annotation = get_args(p.annotation)[1]
        if not hasattr(annotation, "output") or not annotation.output:
            continue

        output_type = type(annotation)
        assert output_type is Artifact or output_type is Parameter

        kwargs: Dict[str, Any] = {}
        if isinstance(output_type, Inputable):
            for attr in output_type.get_input_attributes():
                if hasattr(annotation, attr) and getattr(annotation, attr) is not None:
                    kwargs[attr] = getattr(annotation, attr)
        else:
            raise ValueError(f"The output {output_type} cannot be an input annotation.")

        # use the function parameter name when not provided by user
        if "name" not in kwargs:
            kwargs["name"] = name

        new_object = output_type(**kwargs)

        if isinstance(get_args(p.annotation)[1], Artifact):
            artifacts.append(new_object)
        elif isinstance(get_args(p.annotation)[1], Parameter):
            parameters.append(new_object)

    return parameters, artifacts


def _get_parameters_and_artifacts_from_callable(source: Callable) -> Tuple[List[Parameter], List[Artifact]]:
    """Look through the function signature and find all Parameters and Artifacts *not* annotated as output."""
    parameters = []
    artifacts = []

    for p in inspect.signature(source).parameters.values():
        if get_origin(p.annotation) is Annotated and isinstance(get_args(p.annotation)[1], Artifact):
            annotation = get_args(p.annotation)[1]
            if hasattr(annotation, "output") and annotation.output:
                continue
            mytype = type(annotation)
            kwargs = {}
            for attr in mytype.get_input_attributes():
                if hasattr(annotation, attr) and getattr(annotation, attr) is not None:
                    kwargs[attr] = getattr(annotation, attr)

            artifact = mytype(**kwargs)
            artifacts.append(artifact)
        else:
            if p.default != inspect.Parameter.empty and p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                default = p.default
            else:
                default = MISSING

            param = Parameter(name=p.name, default=default)
            parameters.append(param)

            if get_origin(p.annotation) is not Annotated:
                continue

            annotation = get_args(p.annotation)[1]

            if hasattr(annotation, "output") and annotation.output:
                parameters.pop()
                continue

            if not isinstance(annotation, Parameter):
                continue

            for attr in Parameter.get_input_attributes():
                if not hasattr(annotation, attr) or getattr(annotation, attr) is None:
                    continue

                if attr == "default" and param.default is not None:
                    raise ValueError(
                        "The default cannot be set via both the function parameter default and the annotation's default"
                    )
                setattr(param, attr, getattr(annotation, attr))

    return parameters, artifacts


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

    Returns:
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

        Returns:
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
            """Invokes a `Script` object's `__call__` method using the given `task_params`."""
            if _context.active:
                return s.__call__(*args, **kwargs)
            return func(*args, **kwargs)

        # Set the wrapped function to the original function so that we can use it later
        task_wrapper.wrapped_function = func  # type: ignore
        return task_wrapper

    return script_wrapper


def extract_output_annotations(function: Callable) -> Optional[List]:
    """Extract the output annotations out of the function signature."""
    output = []
    origin_type = get_origin(inspect.signature(function).return_annotation)
    annotation_args = get_args(inspect.signature(function).return_annotation)
    if origin_type is Annotated:
        output.append(annotation_args)
    elif origin_type is tuple:
        for annotation in annotation_args:
            output.append(get_args(annotation))

    return output or None


class InlineScriptConstructor(ScriptConstructor):
    """`InlineScriptConstructor` is a script constructor that submits a script as a `source` to Argo.

    This script constructor is focused on taking a Python script/function "as is" for remote execution. The
    constructor processes the script to infer what parameters it needs to deserialize so the script can execute.
    The submitted script will contain prefixes such as new imports, e.g. `import os`, `import json`, etc. and
    will contain the necessary `json.loads` calls to deserialize the parameters so they are usable by the script just
    like a normal Python script/function.
    """

    add_cwd_to_sys_path: Optional[bool] = None

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
        content = roundtrip(inspect.getsource(instance.source)).splitlines()
        for i, line in enumerate(content):
            if line.startswith("def") or line.startswith("async def"):
                break

        s = "\n".join(content[i + 1 :])
        script += textwrap.dedent(s)
        return textwrap.dedent(script)


class RunnerScriptConstructor(ScriptConstructor, ExperimentalMixin):
    """`RunnerScriptConstructor` is a script constructor that runs a script in a container.

    The runner script, also known as "The Hera runner", takes a script/Python function definition, inferts the path
    to the function (module import), assembles a path to invoke the function, and passes any specified parameters
    to the function. This helps users "save" on the `source` space required for submitting a function for remote
    execution on Argo. Execution within the container *requires* the executing container to include the file that
    contains the submitted script. More specifically, the container must be created in some process (e.g. CI), so that
    it conains the script to run remotely.
    """

    _flag: str = "script_runner"

    outputs_directory: str = "hera/outputs"
    """Used for saving outputs when defined using annotations."""

    def transform_values(self, cls: Type[Script], values: Any) -> Any:
        """A function that can inspect the Script instance and generate the source field."""
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
        """A function that can inspect the Script instance and generate the source field."""
        return f"{g.inputs.parameters:$}"


__all__ = ["Script", "script", "ScriptConstructor", "InlineScriptConstructor", "RunnerScriptConstructor"]
