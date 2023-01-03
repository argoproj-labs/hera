"""The implementation of a Hera task for Argo workflows"""

import copy
import inspect
import json
import textwrap
from typing import Callable, Dict, List, Optional, Union, cast

import hera
from hera.dag import DAG
from hera.env import Env
from hera.global_config import GlobalConfig
from hera.image import ImagePullPolicy
from hera.models import *
from hera.operator import Operator
from hera.validators import validate_name
from hera.workflow_status import WorkflowStatus


class TaskResult(str, Enum):
    Failed = "Failed"
    Succeeded = "Succeeded"
    Errored = "Errored"
    Skipped = "Skipped"
    Omitted = "Omitted"
    Daemoned = "Daemoned"
    AnySucceeded = "AnySucceeded"
    AllFailed = "AllFailed"

    def __str__(self):
        return str(self.value)


class Task:
    def __init__(
        self,
        name: str,
        args: Optional[List[str]] = None,
        command: Optional[List[str]] = None,
        env: Optional[List[v1.EnvVar]] = None,
        env_from: Optional[List[v1.EnvFromSource]] = None,
        image: Optional[str] = None,
        image_pull_policy: Optional[str] = None,
        lifecycle: Optional[v1.Lifecycle] = None,
        liveness_probe: Optional[v1.Probe] = None,
        ports: Optional[List[v1.ContainerPort]] = None,
        readiness_probe: Optional[v1.Probe] = None,
        resources: Optional[v1.ResourceRequirements] = None,
        security_context: Optional[v1.SecurityContext] = None,
        source: Optional[Union[Callable, str]] = None,
        startup_probe: Optional[v1.Probe] = None,
        stdin: Optional[bool] = None,
        stdin_once: Optional[bool] = None,
        termination_message_path: Optional[str] = None,
        termination_message_policy: Optional[str] = None,
        tty: Optional[bool] = None,
        volume_devices: Optional[List[v1.VolumeDevice]] = None,
        volume_mounts: Optional[List[v1.VolumeMount]] = None,
        working_dir: Optional[str] = None,
        arguments: Optional[List[Union[Parameter, Artifact]]] = None,
        continue_on: Optional[ContinueOn] = None,
        dependencies: Optional[List[str]] = None,
        depends: Optional[str] = None,
        hooks: Optional[Dict[str, LifecycleHook]] = None,
        inline: Optional[Template] = None,
        on_exit: Optional[str] = None,
        template: Optional[str] = None,
        template_ref: Optional[TemplateRef] = None,
        when: Optional[str] = None,
        with_items: Optional[List[Item]] = None,
        with_param: Optional[str] = None,
        with_sequence: Optional[Sequence] = None,
        active_deadline_seconds: Optional[intstr.IntOrString] = None,
        affinity: Optional[v1.Affinity] = None,
        archive_location: Optional[ArtifactLocation] = None,
        automount_service_account_token: Optional[bool] = None,
        container: Optional[v1.Container] = None,
        container_set: Optional[ContainerSetTemplate] = None,
        daemon: Optional[bool] = None,
        dag: Optional[DAG] = None,
        data: Optional[Data] = None,
        executor: Optional[ExecutorConfig] = None,
        fail_fast: Optional[bool] = None,
        host_aliases: Optional[List[v1.HostAlias]] = None,
        http: Optional[HTTP] = None,
        init_containers: Optional[List[UserContainer]] = None,
        inputs: Optional[
            Union[
                List[Union[Parameter, Artifact]],
                List[Union[Parameter, Artifact, Dict[str, Any]]],
                Dict[str, Any],
            ]
        ] = None,
        outputs: Optional[List[Union[Parameter, Artifact]]] = None,
        exit_code: Optional[str] = None,
        result: Optional[str] = None,
        memoize: Optional[Memoize] = None,
        metadata: Optional[Metadata] = None,
        metrics: Optional[Union[Prometheus, Metrics]] = None,
        node_selector: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None,
        labels: Optional[Dict[str, str]] = None,
        parallelism: Optional[int] = None,
        plugin: Optional[Plugin] = None,
        pod_spec_patch: Optional[str] = None,
        priority: Optional[int] = None,
        priority_class_name: Optional[str] = None,
        resource: Optional[ResourceTemplate] = None,
        retry_strategy: Optional[RetryStrategy] = None,
        scheduler_name: Optional[str] = None,
        service_account_name: Optional[str] = None,
        sidecars: Optional[List[UserContainer]] = None,
        suspend: Optional[SuspendTemplate] = None,
        synchronization: Optional[Synchronization] = None,
        timeout: Optional[str] = None,
        tolerations: Optional[List[v1.Toleration]] = None,
        volumes: Optional[List[v1.Volume]] = None,
    ):
        if dag and source:
            raise ValueError("Cannot use both `dag` and `source`")
        if dag and template_ref:
            raise ValueError("Cannot use both `dag` and `template_ref`")
        if dag and suspend:
            raise ValueError("Cannot use both `dag` and `suspend`")
        if with_param is not None and with_sequence is not None:
            raise ValueError("Cannot use both `with_sequence` and `with_param`")

        self.name: str = validate_name(name)
        self.args: Optional[List[str]] = args
        self.command: Optional[List[str]] = command
        self.env: Optional[List[v1.EnvVar]] = env
        self.env_from: Optional[List[v1.EnvFromSource]] = env_from
        self.image: Optional[str] = image or GlobalConfig.image
        self.image_pull_policy: Optional[str] = image_pull_policy or ImagePullPolicy.always.value
        self.lifecycle: Optional[v1.Lifecycle] = lifecycle
        self.liveness_probe: Optional[v1.Probe] = liveness_probe
        self.ports: Optional[List[v1.ContainerPort]] = ports
        self.readiness_probe: Optional[v1.Probe] = readiness_probe
        self.resources: Optional[v1.ResourceRequirements] = resources
        self.security_context: Optional[v1.SecurityContext] = security_context
        self.source: Optional[Union[Callable, str]] = source
        self.startup_probe: Optional[v1.Probe] = startup_probe
        self.stdin: Optional[bool] = stdin
        self.stdin_once: Optional[bool] = stdin_once
        self.termination_message_path: Optional[str] = termination_message_path
        self.termination_message_policy: Optional[str] = termination_message_policy
        self.tty: Optional[bool] = tty
        self.volume_devices: Optional[List[v1.VolumeDevice]] = volume_devices
        self.volume_mounts: Optional[List[v1.VolumeMount]] = volume_mounts
        self.working_dir: Optional[str] = working_dir
        self.arguments: Optional[List[Artifact, Parameter]] = arguments
        self.continue_on: Optional[ContinueOn] = continue_on
        self.dependencies: Optional[List[str]] = dependencies
        self.depends: Optional[str] = depends
        self.hooks: Optional[Dict[str, LifecycleHook]] = hooks
        self.inline: Optional[Template] = inline
        self.on_exit: Optional[str] = on_exit
        self.template: Optional[str] = template
        self.template_ref: Optional[TemplateRef] = template_ref
        self.when: Optional[str] = when
        self.with_items: Optional[List[Item]] = with_items
        self.with_param: Optional[str] = with_param
        self.with_sequence: Optional[Sequence] = with_sequence
        self.active_deadline_seconds: Optional[intstr.IntOrString] = active_deadline_seconds
        self.affinity: Optional[v1.Affinity] = affinity
        self.archive_location: Optional[ArtifactLocation] = archive_location
        self.automount_service_account_token: Optional[bool] = automount_service_account_token
        self.container: Optional[v1.Container] = container
        self.container_set: Optional[ContainerSetTemplate] = container_set
        self.daemon: Optional[bool] = daemon
        self.dag: Optional[DAGTemplate] = dag
        self.data: Optional[Data] = data
        self.executor: Optional[ExecutorConfig] = executor
        self.fail_fast: Optional[bool] = fail_fast
        self.host_aliases: Optional[List[v1.HostAlias]] = host_aliases
        self.http: Optional[HTTP] = http
        self.init_containers: Optional[List[UserContainer]] = init_containers
        self.inputs: Optional[
            Union[
                List[Union[Parameter, Artifact]],
                List[Union[Parameter, Artifact, Dict[str, Any]]],
                Dict[str, Any],
            ]
        ] = self._parse_inputs(inputs)
        self.outputs: Optional[List[Union[Parameter, Artifact]]] = outputs or []
        self.exit_code: Optional[str] = exit_code
        self.result: Optional[str] = result
        self.memoize: Optional[Memoize] = memoize
        self.metadata: Optional[Metadata] = metadata
        self.metrics: Optional[Metrics] = self._parse_metrics(metrics)
        self.node_selector: Optional[Dict[str, str]] = node_selector
        self.annotations: Optional[Dict[str, str]] = annotations
        self.labels: Optional[Dict[str, str]] = labels
        self.parallelism: Optional[int] = parallelism
        self.plugin: Optional[Plugin] = plugin
        self.pod_spec_patch: Optional[str] = pod_spec_patch
        self.priority: Optional[int] = priority
        self.priority_class_name: Optional[str] = priority_class_name
        self.resource: Optional[ResourceTemplate] = resource
        self.retry_strategy: Optional[RetryStrategy] = retry_strategy
        self.scheduler_name: Optional[str] = scheduler_name
        self.service_account_name: Optional[str] = service_account_name
        self.sidecars: Optional[List[UserContainer]] = sidecars
        self.suspend: Optional[SuspendTemplate] = suspend
        self.synchronization: Optional[Synchronization] = synchronization
        self.timeout: Optional[str] = timeout
        self.tolerations: Optional[List[v1.Toleration]] = tolerations
        self.volumes: Optional[List[v1.Volume]] = volumes

        self.dag = dag
        self.source = source
        self.memoize = memoize
        self.volumes = volumes or []
        self.inputs = [] if inputs is None else self._parse_inputs(inputs)
        self.outputs = outputs or []
        self.env = env or []
        self.with_param = with_param
        self.with_sequence = with_sequence
        self.pod_spec_patch = pod_spec_patch
        self.resource_template: Optional[ResourceTemplate] = resource
        self.active_deadline_seconds: Optional[int] = active_deadline_seconds
        self.timeout: Optional[str] = timeout
        self.resources = resources

        self.exit_task: Optional[str] = None
        self.is_exit_task: bool = False

        self.validate()

        # here we cast for otherwise `mypy` complains that Hera adds an incompatible type with a dictionary, which is
        # an acceptable type for the `inputs` field upon `init`
        self.inputs = cast(List[Union[Parameter, Artifact]], self.inputs)
        self.inputs += self._deduce_input_params()

        if hera.dag_context.is_set():
            hera.dag_context.add_task(self)

        for hook in GlobalConfig.task_post_init_hooks:
            hook(self)

    def _parse_metrics(self, metrics: Optional[Union[Prometheus, Metrics]]) -> Optional[Metrics]:
        """Parses provided combination of metrics into a single `Metrics` object.

        Parameters
        ----------
        metrics: Optional[Union[Prometheus, Metrics]]
            Optional `Metrics` or single `Prometheus` instance to convert into `Metrics`.

        Returns
        -------
        Optional[Metrics]
            Constructed `Metrics`.
        """
        if metrics is None:
            return None
        if isinstance(metrics, Prometheus):
            return Metrics(prometheus=[metrics])
        elif isinstance(metrics, list):
            assert all([isinstance(m, Prometheus) for m in metrics])
            return Metrics(prometheus=metrics)
        elif isinstance(metrics, Metrics):
            return metrics
        raise ValueError(
            "Unknown type provided for `metrics`, expected type is `Optional[Union[Metric, List[Metric], Metrics]]`,"
            f"received {type(metrics)}"
        )

    def _parse_inputs(
        self,
        inputs: Optional[
            Union[List[Union[Parameter, Artifact]], List[Union[Parameter, Artifact, Dict[str, Any]]], Dict[str, Any]]
        ],
    ) -> List[Union[Parameter, Artifact]]:
        """Parses the dictionary aspect of the specified inputs and returns a list of parameters and artifacts.

        Parameters
        ----------
        inputs: Union[Dict[str, Any], List[Union[Parameter, Artifact, Dict[str, Any]]]]
            The list of inputs specified on the task. The `Dict` aspect is treated as a mapped collection of
            Parameters. If a single dictionary is specified, all the fields are transformed into `Parameter`s. The key
            is the `name` of the `Parameter` and the `value` is the `value` field of the `Parameter.

        Returns
        -------
        List[Union[Parameter, Artifact]]
            A list of parameters and artifacts. The parameters contain the specified dictionary mapping as well, as
            independent parameters.
        """
        if inputs is None:
            return []

        result: List[Union[Parameter, Artifact]] = []
        if isinstance(inputs, dict):
            for k, v in inputs.items():
                result.append(Parameter(name=k, value=v))
        else:
            for i in inputs:
                if isinstance(i, Parameter) or isinstance(i, Artifact):
                    result.append(i)
                elif isinstance(i, dict):
                    for k, v in i.items():
                        result.append(Parameter(name=k, value=v))
        return result

    @property
    def id(self) -> str:
        """Unique ID of container task.

        See Also
        --------
        https://argoproj.github.io/argo-workflows/variables/#dag-templates
        """
        return f"{{{{tasks.{self.name}.id}}}}"

    @property
    def ip(self) -> str:
        """IP address of the daemon container task.

        See Also
        --------
        https://argoproj.github.io/argo-workflows/variables/#dag-templates
        """
        return f"{{{{tasks.{self.name}.ip}}}}"

    @property
    def status(self) -> str:
        """Phase status of the task.

        See Also
        --------
        https://argoproj.github.io/argo-workflows/variables/#dag-templates
        """
        return f"{{{{tasks.{self.name}.status}}}}"

    @property
    def exit_code(self) -> str:
        """Exit code of script or container task.

        See Also
        --------
        https://argoproj.github.io/argo-workflows/variables/#dag-templates
        """
        return f"{{{{tasks.{self.name}.exitCode}}}}"

    @property
    def started_at(self) -> str:
        """Time-stamp when the task started.

        See Also
        --------
        https://argoproj.github.io/argo-workflows/variables/#dag-templates
        """
        return f"{{{{tasks.{self.name}.startedAt}}}}"

    @property
    def finished_at(self) -> str:
        """Time-stamp when the task finished.

        See Also
        --------
        https://argoproj.github.io/argo-workflows/variables/#dag-templates
        """
        return f"{{{{tasks.{self.name}.finishedAt}}}}"

    def _get_dependency_tasks(self) -> List[str]:
        """Extract task names from `depends` string"""
        if self.depends is None:
            return []
        # Filter out operators
        all_operators = [o for o in Operator]
        tasks = [t for t in self.depends.split() if t not in all_operators]
        # Remove dot suffixes
        task_names = [t.split(".")[0] for t in tasks]
        return task_names

    def next(self, other: "Task", operator: Operator = Operator.and_, on: Optional[TaskResult] = None) -> "Task":
        """Sets this task as a dependency of the other passed task.

        Parameters
        ----------
        other: Task
            The other task to set a dependency for. The new dependency of the task is this task.
        operator: Operator = Operator.and_
            Operator to apply on the result.
        on: Optional[TaskResult] = None
            The task result to perform the `operator` on.

        Returns
        -------
        Task
            The other task that was specified.

        Examples
        --------
        t1, t2, t3 = Task('t1'), Task('t2'), Task('t3')
        t1.next(t2).next(t3)
        """
        assert issubclass(other.__class__, Task)

        condition = f".{on}" if on else ""
        if other.depends is None:
            # First dependency
            other.depends = self.name + condition
        elif self.name in other._get_dependency_tasks():
            raise ValueError(f"{self.name} already in {other.name}'s depends: {other.depends}")
        else:
            # Add follow-up dependency
            other.depends += f" {operator} {self.name + condition}"
        return other

    def __rrshift__(self, other: List["Task"]) -> "Task":
        """Sets the `other` as a dependency of `self`.

        This method piggybacks on the default fallback mechanism of Python, which invokes `__rrshift__` when
        `__rshift__` fails. Hera uses `__rshift__` (TaskA >> TaskB) for setting task dependency chains. However, that
        does not natively support lists of items/tasks, so this provides the reverse mechanism - the other here is the
        list of upstream dependency of `self`.

        Parameters
        ----------
        other: List["Task"]
            The list of upstream dependencies of this task.

        Returns
        -------
        Task
            This task/`self`.
        """
        assert isinstance(other, list), f"Unknown type {type(other)} specified using reverse right bitshift operator"
        for o in other:
            o.next(self)
        return self

    def __rshift__(self, other: Union["Task", List["Task"]]) -> Union["Task", List["Task"]]:
        """Sets this task as a dependency of the other passed task.

        Parameters
        ----------
        other: Union["Task", List["Task"]]
            The other task(s) to set a dependency for. The new dependency of the task is this task.

        Returns
        -------
        Union["Task", List["Task"]]
            The other task/s that was/were specified as the dependencies.

        Examples
        --------
        t1 = Task('t1')
        t2 = Task('t2')
        t1 >> t2  # this makes t2 execute AFTER t1
        """
        if isinstance(other, Task):
            return self.next(other)
        elif isinstance(other, list):
            for o in other:
                assert isinstance(
                    o, Task
                ), f"Unknown list item type {type(o)} specified using right bitshift operator `>>`"
                self.next(o)
            return other
        raise ValueError(f"Unknown type {type(other)} provided to `__rshift__`")

    def on_workflow_status(self, status: WorkflowStatus, op: Operator = Operator) -> "Task":
        """Execute this task conditionally on a workflow status."""
        expression = f"{{{{workflow.status}}}} {op} {status}"
        if self.when:
            self.when += f" {Operator.and_} {expression}"
        else:
            self.when = expression
        return self

    def on_success(self, other: "Task") -> "Task":
        """Execute `other` when this task succeeds"""
        return self.next(other, on=TaskResult.Succeeded)

    def on_failure(self, other: "Task") -> "Task":
        """Execute `other` when this task fails"""
        return self.next(other, on=TaskResult.Failed)

    def on_error(self, other: "Task") -> "Task":
        """Execute `other` when this task errors."""
        return self.next(other, on=TaskResult.Errored)

    def on_exit(self, other: Union["Task", DAG]) -> "Task":
        """Execute `other` on completion (exit) of this Task."""
        # in instances when `other` contains a DAG it is the DAG that needs a template to be
        # created. Therefore, this "resets" the `other` to be the DAG that needs to be used
        if isinstance(other, Task) and other.dag is not None:
            raise ValueError(
                "Provided `Task` contains a `DAG` set. Only `Task`s with `source` are supported or pure `DAG`s. "
                "Try passing in `Task.dag` or set `source` on `Task` if you have a single task to run on exit."
            )

        if isinstance(other, Task):
            self.exit_task = other.name
            other.is_exit_task = True
        elif isinstance(other, DAG):
            # If the exit task is a DAG, we need to propagate the DAG and its
            # templates by instantiating a task within the current context.
            # The name will never be used; it's only present because the
            # field is mandatory.
            t = Task("temp-name-for-hera-exit-dag", dag=other)
            t.is_exit_task = True
            self.exit_task = other.name
        else:
            raise ValueError(f"Unrecognized exit type {type(other)}, supported types are `Task` and `DAG`")
        return self

    def on_other_result(self, other: "Task", value: str, operator: Operator = Operator.equals) -> "Task":
        """Execute this task based on the `other` result"""
        expression = f"'{other.get_result()}' {operator} {value}"
        if self.when:
            self.when += f" {Operator.and_} {expression}"
        else:
            self.when = expression
        other.next(self)
        return self

    def when_any_succeeded(self, other: "Task") -> "Task":
        """Sets the other task to execute when any of the tasks of this task group have succeeded.

        Parameters
        ----------
        other: Task
            The other task to execute when any of the tasks of this task group have succeeded.

        Returns
        -------
        Task
            The current task.

        Raises
        ------
        AssertionError
            When the task does not contain multiple `func_params` to process.
            When the task does not use `input_from`.
            When the task uses `continue_on_fail` or `continue_on_error`.

        Notes
        -----
        See: https://argoproj.github.io/argo-workflows/enhanced-depends-logic/
        """
        assert (self.with_param is not None) or (
            self.with_sequence is not None
        ), "Can only use `when_all_failed` when using `with_param` or `with_sequence`"

        return self.next(other, on=TaskResult.AnySucceeded)

    def when_all_failed(self, other: "Task") -> "Task":
        """Sets the other task to execute when all the tasks of this task group have failed

        Parameters
        ----------
        other: Task
            The other task to execute when all of the tasks of this task group have failed.

        Returns
        -------
        Task
            The current task.

        Raises
        ------
        AssertionError
            When the task does not contain multiple `func_params` to process.
            When the task does not use `input_from`.
            When the task uses `continue_on_fail` or `continue_on_error`.

        Notes
        -----
        See: https://argoproj.github.io/argo-workflows/enhanced-depends-logic/
        """
        assert (self.with_param is not None) or (
            self.with_sequence is not None
        ), "Can only use `when_all_failed` when using `with_param` or `with_sequence`"

        return self.next(other, on=TaskResult.AllFailed)

    def _validate_io(self):
        """
        Validates that the given function and corresponding params fit one another, raises AssertionError if
        conditions are not satisfied.
        """
        i_parameters = [obj for obj in self.inputs if isinstance(obj, Parameter)]
        i_artifacts = [obj for obj in self.inputs if isinstance(obj, Artifact)]
        assert len(set([i.name for i in i_parameters])) == len(i_parameters), "input parameters must have unique names"
        assert len(set([i.name for i in i_artifacts])) == len(i_artifacts), "input artifacts must have unique names"

        o_parameters = [obj for obj in self.outputs if isinstance(obj, Parameter)]
        o_artifacts = [obj for obj in self.outputs if isinstance(obj, Artifact)]
        assert len(set([o.name for o in o_parameters])) == len(
            o_parameters
        ), "output parameters must have unique names"
        assert len(set([o.name for o in o_artifacts])) == len(o_artifacts), "output artifacts must have unique names"

    def validate(self):
        """
        Validates that the given function and corresponding params fit one another, raises AssertionError if
        conditions are not satisfied.
        """
        self._validate_io()
        if self.with_param is not None:
            assert isinstance(self.with_param, list) or isinstance(
                self.with_param, str
            ), "`with_param` is of unsupported type"
            assert len(self.with_param) != 0, "`with_param` cannot be empty"
        if self.with_sequence is not None:
            assert isinstance(self.with_sequence, Sequence), "Accepted type for `with_sequence` is `Sequence`"
        if self.source:
            self._validate_source()
        if self.pod_spec_patch is not None:
            if not isinstance(self.pod_spec_patch, str):
                raise ValueError("`pod_spec_patch` must be `str` to handle argo expressions properly")

    def _validate_source(self):
        if callable(self.source):
            args = set(inspect.getfullargspec(self.source).args)
            if self.memoize:
                assert self.memoize.key in args, "memoize key must be a parameter of the function"

    def _build_arguments(self) -> Optional[Arguments]:
        """Assembles and returns the task arguments"""
        parameters = [obj for obj in self.inputs if isinstance(obj, Parameter)]
        parameters = [p for p in parameters if p is not None]  # Some parameters might not resolve
        artifacts = [obj for obj in self.inputs if isinstance(obj, Artifact)]
        if len(parameters) + len(artifacts) == 0:
            # Some inputs do not require arguments (defaults)
            return None
        return Arguments(artifacts=artifacts, parameters=parameters)

    def get_parameters_as(self, name):
        """Gets all the output parameters from this task"""
        return Parameter(name=name, value=f"{{{{tasks.{self.name}.outputs.parameters}}}}")

    def get_parameter(self, name: str) -> Parameter:
        """Returns a Parameter from the task's outputs based on the name.

        Parameters
        ----------
        name: str
            The name of the parameter to extract as an output.
        Returns
        -------
        Parameter
            Parameter with the same name

        """
        parameters = [p for p in self.outputs if isinstance(p, Parameter)]
        obj = next((output for output in parameters if output.name == name), None)
        if obj is not None:
            if isinstance(obj, Parameter):
                value = f"{{{{tasks.{self.name}.outputs.parameters.{name}}}}}"
                return Parameter(name=name, value=value, default=obj.default)
            raise NotImplementedError(type(obj))
        raise KeyError(f"No output parameter named `{name}` found")

    def get_artifact(self, name: str) -> Artifact:
        """Returns an Artifact from this tasks' outputs based on the name.

        Parameters
        ----------
        name: str
            The name of the parameter to extract as an output.

        Returns
        -------
        Artifact
            Artifact with the same name

        """
        artifacts = [p for p in self.outputs if isinstance(p, Artifact)]
        obj = next((output for output in artifacts if output.name == name), None)
        if obj is not None:
            if isinstance(obj, Artifact):
                return Artifact(name=name, path=obj.path, from_=f"{{{{tasks.{self.name}.outputs.artifacts.{name}}}}}")
            raise NotImplementedError(type(obj))
        raise KeyError(f"No output artifact named `{name}` found")

    def get_result(self) -> str:
        """Returns the formatted field that points to the result/output of this task"""
        return f"{{{{tasks.{self.name}.outputs.result}}}}"

    def get_output_condition(self, operator: Operator, value: str) -> str:
        """Returns the output condition of the task based on the specified operator and value"""
        return f"{self.get_result()} {operator} {value}"

    def get_result_as(self, name: str) -> Parameter:
        return Parameter(name=name, value=f"{{{{tasks.{self.name}.outputs.result}}}}")

    def get_command(self) -> Optional[List]:
        """
        Parses and returns the specified task command. This will attempt to stringify every command option and
        raise a ValueError on failure. This defaults to Python if `command` and `args` are not specified.
        """
        if not self.command and not self.args:
            return ["python"]
        elif not self.command:
            return None
        return [str(cc) for cc in self.command]

    def get_args(self) -> Optional[List[str]]:
        """Returns the arguments of the task"""
        if self.args is None:
            return None
        return [str(arg) for arg in self.args]

    def _deduce_input_params_from_source(self) -> List[Parameter]:
        """
        Returns a list of generated Parameters based on the function signature
        in combination with `with_params` or `with_sequence`
        """
        if self.source is None or isinstance(self.source, str):
            return []
        assert callable(self.source), "`source` is not a callable function"

        # If there are any kwargs arguments associated with the function signature,
        # we store these as we can set them as default values for argo arguments
        source_signature: Dict[str, Optional[str]] = {}
        for p in inspect.signature(self.source).parameters.values():
            if p.default != inspect.Parameter.empty and p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                source_signature[p.name] = p.default
            else:
                source_signature[p.name] = None

        # Deduce input parameters from function source. Only add those which haven't been explicitly set in inputs
        input_params_names = [p.name for p in self.inputs if isinstance(p, Parameter)]
        deduced_params: List[Parameter] = [
            Parameter(name=n, default=v) for n, v in source_signature.items() if n not in input_params_names
        ]

        # Find owners to the deduced parameters. They could exist in either:
        #   - with_param
        #   - with_sequence

        non_default_params = [p for p in deduced_params if p.default is None]

        if self.with_sequence is not None:
            if len(non_default_params) == 1:
                # Non-ambiguous mapping; `with_sequence` yields non-nested items.
                non_default_params.pop().value = "{{item}}"

        if self.with_param is not None:
            if isinstance(self.with_param, str) or isinstance(self.with_param, Parameter):
                # with_param is a string-list or an argo reference (str) to something that resolves into a list.
                # We assume that each (resolved) object contains all arguments for function:

                if len(non_default_params) == 1:
                    # We assume the user wants the entire object in the non-default argument
                    non_default_params.pop().value = "{{item}}"
                else:
                    # We assume that there are sub-items which have names
                    # corresponding to the source signature
                    while len(non_default_params) != 0:
                        parameter = non_default_params.pop()
                        parameter.value = f"{{{{item.{parameter.name}}}}}"

            elif isinstance(self.with_param, list):
                assert self.with_param is not None
                first_param = self.with_param[0]
                if not all(isinstance(x, type(first_param)) for x in self.with_param):
                    raise ValueError("Non-homogeneous types in `with_param`")

                # All elements are of same type
                if isinstance(first_param, dict):
                    # Validate that the dicts contain required keys
                    first_param_keys = first_param.keys()
                    required_keys = [p.name for p in deduced_params if not p.default]
                    for p in self.with_param:
                        missing_args = set(required_keys) - p.keys()  # type: ignore
                        assert (
                            len(first_param_keys ^ p.keys()) == 0  # type: ignore
                        ), "`with_param` contains dicts with different set of keys"
                        if missing_args:
                            raise ValueError(f"param in `with_params` is missing non-default argument: {missing_args}")

                    # Map non-default params to nested items
                    while len(non_default_params) != 0:
                        parameter = non_default_params.pop()
                        parameter.value = f"{{{{item.{parameter.name}}}}}"

                    # Override possible defaults based observed keys
                    for default_parameter in [p for p in deduced_params if p.default]:
                        if default_parameter.name in first_param_keys:
                            default_parameter.value = f"{{{{item.{default_parameter.name}}}}}"

                else:  # Assuming list of objects which can be converted to str
                    if len(non_default_params) == 1:
                        non_default_params.pop().value = "{{item}}"

        if (self.with_param is not None) or (self.with_sequence is not None):
            # Verify that we're utilizing 'item'
            if not any([p.contains_item for p in self.inputs + deduced_params]):  # type: ignore
                raise ValueError(
                    "`with_param` or `with_sequence` items are utilized in inputs, nor could they be deduced"
                )

        return deduced_params

    def _deduce_input_params(
        self,
    ) -> List[Parameter]:
        """Deduce missing input parameters based on the contents of:
            - `inputs`
            - `with_param`
            - `with_sequence`
            - `source`
            - `env`

        Returns
        -------
        List[Parameter]
            A list representing the deduced parameters.
        """
        deduced_params: List[Parameter] = []

        if self.dag:
            if self.dag.inputs:
                self.dag.inputs = cast(List[Union[Parameter, Artifact]], self.dag.inputs)
                if len(self.dag.inputs) == 1:
                    deduced_params.append(Parameter(name=self.dag.inputs[0].name, value="{{item}}"))
                else:
                    for p in self.dag.inputs:
                        deduced_params.append(Parameter(name=p.name, value=f"{{{{item.{p.name}}}}}"))
        else:
            deduced_params += self._deduce_input_params_from_source()

        for spec in self.env:
            if isinstance(spec, Env) and spec.value_from_input is not None:
                value = (
                    spec.value_from_input.value
                    if isinstance(spec.value_from_input, Parameter)
                    else spec.value_from_input
                )
                deduced_params.append(Parameter(name=spec.param_name, value=value))

        return deduced_params

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
        inputs = [i for i in self.inputs if isinstance(i, Parameter)]
        inputs = [a for a in inputs if a is not None]
        extract = "import json\n"
        for param in sorted(inputs, key=lambda x: x.name):
            # Hera does not know what the content of the `InputFrom` is, coming from another task. In some cases
            # non-JSON encoded strings are returned, which fail the loads, but they can be used as plain strings
            # which is why this captures that in an except. This is only used for `InputFrom` cases as the extra
            # payload of the script is not necessary when regular input is set on the task via `func_params`
            extract += f"""try: {param.name} = json.loads('''{{{{inputs.parameters.{param.name}}}}}''')\n"""
            extract += f"""except: {param.name} = '''{{{{inputs.parameters.{param.name}}}}}'''\n"""
        return textwrap.dedent(extract)

    def _get_script(self) -> str:
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
                input_params_names = [p.name for p in self.inputs if isinstance(p, Parameter)]
                missing_args = set(args) - set(input_params_names)
                if missing_args:
                    raise ValueError(f"Missing inputs for source args: {missing_args}")
                kwargs = {name: f"{{{{inputs.parameters.{name}}}}}" for name in args}
                # Resolve the function to a string
                return self.source(**kwargs)
            else:
                # Argo will save the script as a file and run it with cmd:
                # - python /argo/staging/script
                # However, this prevents the script from importing modules in its cwd,
                # since it's looking for files relative to the script path.
                # We fix this by appending the cwd path to sys:
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

    def _build_volume_mounts(self) -> List[VolumeMount]:
        """Assembles the list of volumes to be mounted by the task.

        Returns
        -------
        List[VolumeMount]
            The list of volume mounts to be added to the task specification.
        """
        return [v._build_mount() for v in self.volumes]

    def _build_volume_claim_templates(self) -> List[PersistentVolumeClaim]:
        """Assembles the list of volume claim templates to be created for the task."""
        return [v._build_claim_spec() for v in self.volumes if isinstance(v, Volume)]

    def _build_persistent_volume_claims(self) -> List[ArgoVolume]:
        """Assembles the list of Argo volume specifications"""
        return [
            v._build_claim_spec()
            for v in self.volumes
            if isinstance(v, ExistingVolume)
            or isinstance(v, SecretVolume)
            or isinstance(v, EmptyDirVolume)
            or isinstance(v, ConfigMapVolume)
        ]

    def _build_container_kwargs(self) -> Dict:
        """Assemble the kwargs which will be used as a base for both script and container"""
        pull_policy = None
        if self.image_pull_policy:
            pull_policy = self.image_pull_policy

        kwargs = dict(
            image=self.image,
            image_pull_policy=pull_policy,
            command=self.get_command(),
            resources=self.resources,
            args=self.get_args(),
            env=self.env,
            env_from=self.env_from,
            working_dir=self.working_dir,
            volume_mounts=self._build_volume_mounts(),
            security_context=self.security_context,
        )
        return {k: v for k, v in kwargs.items() if v}  # treats empty lists/None as false

    def _build_script(self) -> ScriptTemplate:
        """Assembles and returns the script template that contains the definition of the script to run in a task.

        Returns
        -------
        ScriptTemplate
            The script template representation of the task.
        """
        return ScriptTemplate(**self._build_container_kwargs(), source=self._get_script())

    def _build_container(self) -> Container:
        """Assembles and returns the container for the task to run in.

        Returns
        -------
        Container
            The container template representation of the task.
        """
        container_args = self._build_container_kwargs()
        container = Container(**container_args)
        return container

    def _build_template(self) -> Optional[Template]:
        """Assembles and returns the template that contains the specification of the parameters, inputs, and other
        configuration required for the task be executed.

        Returns
        -------
        Template
            The template representation of the task.
        """
        if self.template_ref is not None:
            # Template already exists in cluster
            return None
        if self.dag is not None:
            return None

        template = Template(
            active_deadline_seconds=self.active_deadline_seconds,
            affinity=self.affinity,
            archive_location=self.archive_location,
            automount_service_account_token=self.automount_service_account_token,
            daemon=self.daemon,
            dag=self.dag,
            executor=self.executor,
            fail_fast=self.fail_fast,
            host_aliases=self.host_aliases,
            http=self.http,
            init_containers=self.init_containers,
            inputs=Inputs(
                artifacts=list(filter(lambda i: isinstance(i, Artifact), self.inputs)),
                parameters=list(filter(lambda i: isinstance(i, Parameter), self.inputs)),
            ),
            memoize=self.memoize,
            metadata=Metadata(annotations=self.annotations, labels=self.labels),
            metrics=self.metrics,
            name=self.name,
            node_selector=self.node_selector,
            outputs=Outputs(
                artifacts=list(filter(lambda o: isinstance(o, Artifact), self.outputs)),
                parameters=list(filter(lambda o: isinstance(o, Parameter), self.outputs)),
                exit_code=self.exit_code,
                result=self.result,
            ),
            plugin=self.plugin,
            pod_spec_patch=self.pod_spec_patch,
            priority=self.priority,
            priority_class_name=self.priority_class_name,
            resource=self.resource,
            retry_strategy=self.retry_strategy,
            scheduler_name=self.scheduler_name,
            security_context=self.security_context,
            service_account_name=self.service_account_name,
            sidecars=self.sidecars,
            synchronization=self.synchronization,
            timeout=self.timeout,
            tolerations=self.tolerations,
            volumes=self.volumes,
        )

        if self.source is not None:
            setattr(template, "script", self._build_script())
            template.script = self._build_script()
        elif self.resource_template is not None:
            template.resource = self.resource
        else:
            template.container = self._build_container()
        return template

    def _build_dag_task(self) -> DAGTask:
        """Assembles and returns the graph task specification of the task.

        Returns
        -------
        DAGTask
            The graph task representation.
        """
        t = DAGTask(
            arguments=Arguments(
                artifacts=list(filter(lambda a: isinstance(a, Artifact), self.arguments)),
                parameters=list(filter(lambda a: isinstance(a, Parameter), self.arguments)),
            ),
            continue_on=self.continue_on,
            dependencies=self.dependencies,
            depends=self.depends,
            hooks=self.hooks,
            inline=self.inline,
            name=self.name,
            on_exit=self.exit_task,
            when=self.when,
            with_items=self.with_items,
            with_sequence=self.with_sequence,
        )

        if self.template_ref is not None:
            t.template_ref = self.template_ref
        else:
            t.template = self.dag.name if self.dag else self.name

        if self.with_param is not None:
            with_param = self.with_param
            if isinstance(with_param, Parameter):
                with_param = str(with_param)  # this will get the value
            elif not isinstance(self.with_param, str):
                with_param = json.dumps(self.with_param)
            t.with_param = with_param
        return t
