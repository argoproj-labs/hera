"""The script module provides the Script class.

See https://argoproj.github.io/argo-workflows/workflow-concepts/#script
for more on scripts.
"""
import copy
import inspect
import textwrap
from typing import Callable, Dict, List, Optional, Union

from hera.shared import global_config
from hera.workflows._mixins import (
    CallableTemplateMixin,
    ContainerMixin,
    EnvIOMixin,
    ResourceMixin,
    TemplateMixin,
    VolumeMountMixin,
)
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


class Script(
    EnvIOMixin,
    CallableTemplateMixin,
    ContainerMixin,
    TemplateMixin,
    ResourceMixin,
    VolumeMountMixin,
):
    """A Script acts as a wrapper around a container. In Hera this defaults to a "python:3.7" image
    specified by global_config.image, which runs a python source specified by `Script.source`.
    """

    container_name: Optional[str] = None
    args: Optional[List[str]] = None
    command: Optional[List[str]] = global_config.script_command
    lifecycle: Optional[Lifecycle] = None
    security_context: Optional[SecurityContext] = None
    source: Optional[Union[Callable, str]] = None
    working_dir: Optional[str] = None
    add_cwd_to_sys_path: bool = True

    def _get_param_script_portion(self) -> str:
        """Constructs and returns a script that loads the parameters of the specified arguments. Since Argo passes
        parameters through {{input.parameters.name}} it can be very cumbersome for users to manage that. This creates a
        script that automatically imports json and loads/adds code to interpret each independent argument into the
        script.

        Returns
        -------
        str
            The string representation of the script to load.
        """
        inputs = self._build_inputs()
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

    def _build_source(self) -> str:
        """Assembles and returns a script representation of the given function, along with the extra script material
        prefixed to the string. The script is expected to be a callable function the client is interested in submitting
        for execution on Argo and the script_extra material represents the parameter loading part obtained, likely,
        through get_param_script_portion.

        Returns
        -------
        str
            Final formatted script.
        """
        if callable(self.source):
            signature = inspect.signature(self.source)
            args = inspect.getfullargspec(self.source).args
            if signature.return_annotation == str:
                # Resolve function by filling in templated inputs
                input_params_names = [p.name for p in self.inputs if isinstance(p, Parameter)]  # type: ignore
                missing_args = set(args) - set(input_params_names)
                if missing_args:
                    raise ValueError(f"Missing inputs for source args: {missing_args}")
                kwargs = {name: f"{{{{inputs.parameters.{name}}}}}" for name in args}
                # Resolve the function to a string
                return self.source(**kwargs)
            else:
                script = ""
                # Argo will save the script as a file and run it with cmd:
                # - python /argo/staging/script
                # However, this prevents the script from importing modules in its cwd,
                # since it's looking for files relative to the script path.
                # We fix this by appending the cwd path to sys:
                if self.add_cwd_to_sys_path:
                    script = "import os\nimport sys\nsys.path.append(os.getcwd())\n"

                script_extra = self._get_param_script_portion() if args else None
                if script_extra:
                    script += copy.deepcopy(script_extra)
                    script += "\n"

                # content represents the function components, separated by new lines
                # therefore, the actual code block occurs after the end parenthesis, which is a literal `):\n`
                content = inspect.getsourcelines(self.source)[0]
                token_index, start_token = 1, ":\n"
                for curr_index, curr_token in enumerate(content):
                    if start_token in curr_token:
                        # when we find the curr token we find the end of the function header. The next index is the
                        # starting point of the function body
                        token_index = curr_index + 1
                        break

                s = "".join(content[token_index:])
                script += textwrap.dedent(s)
                return textwrap.dedent(script)
        else:
            assert isinstance(self.source, str)
            return self.source

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
        for param in func_parameters:
            if param.name not in already_set_params:
                inputs.parameters = [param] if inputs.parameters is None else inputs.parameters + [param]
        return inputs

    def _build_template(self) -> _ModelTemplate:
        return _ModelTemplate(
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
            metrics=self.metrics,
            name=self.name,
            node_selector=self.node_selector,
            outputs=self._build_outputs(),
            parallelism=self.parallelism,
            plugin=self.plugin,
            pod_spec_patch=self.pod_spec_patch,
            priority=self.priority,
            priority_class_name=self.priority_class_name,
            resource=self._build_resources(),
            retry_strategy=self.retry_strategy,
            scheduler_name=self.scheduler_name,
            script=self._build_script(),
            security_context=self.pod_security_context,
            service_account_name=self.service_account_name,
            sidecars=self.sidecars,
            synchronization=self.synchronization,
            timeout=self.timeout,
            tolerations=self.tolerations,
            volumes=self._build_volumes(),
        )

    def _build_script(self) -> _ModelScriptTemplate:
        return _ModelScriptTemplate(
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
            source=self._build_source(),
            startup_probe=self.startup_probe,
            stdin=self.stdin,
            stdin_once=self.stdin_once,
            termination_message_path=self.termination_message_path,
            termination_message_policy=self.termination_message_policy,
            tty=self.tty,
            volume_devices=self.volume_devices,
            volume_mounts=self._build_volume_mounts(),
            working_dir=self.working_dir,
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

    def script_wrapper(func: Callable) -> Callable:
        """Wraps the given callable into a `Script` object that can be invoked.

        Parameters
        ----------
        func: Callable
            Function to wrap.

        Returns
        -------
        Callable
            Another callable that represents the `Script` object `__call__` method.
        """
        s = Script(name=func.__name__.replace("_", "-"), source=func, **script_kwargs)

        def task_wrapper(**task_params) -> Union[Task, Step]:
            """Invokes a `Script` object's `__call__` method using the given `task_params`"""
            return s.__call__(**task_params)  # type: ignore

        return task_wrapper

    return script_wrapper


__all__ = ["Script", "script"]
