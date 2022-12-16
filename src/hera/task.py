"""The implementation of a Hera task for Argo workflows"""

import copy
import inspect
import json
import textwrap
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast

from argo_workflows.models import (
    Container,
    EnvFromSource,
    EnvVar,
    IoArgoprojWorkflowV1alpha1Arguments,
    IoArgoprojWorkflowV1alpha1DAGTask,
    IoArgoprojWorkflowV1alpha1Metadata,
    IoArgoprojWorkflowV1alpha1ScriptTemplate,
    IoArgoprojWorkflowV1alpha1Template,
    PersistentVolumeClaim,
)
from argo_workflows.models import Toleration as ArgoToleration
from argo_workflows.models import Volume as ArgoVolume
from argo_workflows.models import VolumeMount

import hera
from hera.affinity import Affinity
from hera.artifact import Artifact
from hera.dag import DAG
from hera.env import Env
from hera.env_from import BaseEnvFrom
from hera.global_config import GlobalConfig
from hera.image import ImagePullPolicy
from hera.io import IO
from hera.memoize import Memoize
from hera.metric import Metric, Metrics
from hera.operator import Operator
from hera.parameter import Parameter
from hera.resource_template import ResourceTemplate
from hera.resources import Resources
from hera.retry_strategy import RetryStrategy
from hera.security_context import TaskSecurityContext
from hera.sequence import Sequence
from hera.sidecar import Sidecar
from hera.template_ref import TemplateRef
from hera.toleration import Toleration
from hera.validators import validate_name
from hera.volumes import (
    ConfigMapVolume,
    EmptyDirVolume,
    ExistingVolume,
    SecretVolume,
    Volume,
    _BaseVolume,
)
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


class Task(IO):
    """An Argo task representation. This is used to submit functions to be executed on Argo.

    The task can take a function, along with its parameters, resource configuration, a volume, etc, and submit it for
    remote execution.

    Parameters
    ----------
    name: str
        The name of the task to submit as part of a workflow.
    source: Optional[Union[Callable, str]] = None
        The function to execute remotely. If a string is supplied it is submitted as a literal, otherwise the callable
        is parsed and submitted.
    with_param: Optional[Any] = None
        The parameters of the function to execute. Note that this works together with parallel. If the params are
        constructed using a single list of values and parallel is False, it is going to be interpreted as a single
        function call with the given parameters. Otherwise, if parallel is False and the list of params is a list of
        lists (each list contains a series of values to pass to the function), the task will execute as a task
        group and schedule multiple function calls in parallel.
    with_sequence: Optional[Sequence] = None
        Sequence is similar to `with_param` in that it generates a range of objects. See `hera.sequence.Sequence` or
        https://argoproj.github.io/argo-workflows/fields/#sequence.
    inputs: Optional[
            Union[
                List[Union[Parameter, Artifact]],
                List[Union[Parameter, Artifact, Dict[str, Any]]],
                Dict[str, Any],
            ]
    ] = None,
        `Input` or `Parameter` objects that hold parameter inputs. When a dictionary is specified all the key/value
        pairs will be transformed into `Parameter`s. The `key` will be the `name` field of the `Parameter` while the
        `value` will be the `value` field of the `Parameter.
    outputs: Optional[List[Union[Parameter, Artifact]]] = None
        `Output` objects that dictate the outputs of the task.
    dag: Optional[DAG] = None
        The DAG the task should execute.
    image: Optional[str] = None
        The image to use in the execution of the function.
    image_pull_policy: Optional[ImagePullPolicy] = None
        The image_pull_policy represents the way to tell Kubernetes if your Task needs to pull and image or not.
        In case of local development/testing this can be set to 'Never'.
    daemon: bool = False
        Whether to run the task as a daemon.
    command: Optional[List[str]] = None
        The command to use in the environment where the function runs in order to run the specific function. Note that
        the specified function is parsed, stored as a string, and ultimately placed in a separate file inside the task
        and invoked via `python script_file.py`. Also note, that when neither command nor args are set, the command
        will default to python. This command offers users the opportunity to start up the script in a different way
        e.g `time python` to time execution, `horovodrun -p X` to use horovod from an image that allows training models
        on multiple GPUs, etc.
    args: Optional[List[str]] = None
        Optional list of arguments to run in the container. This can be used as an alternative to command, with the
        advantage of not overriding the set entrypoint of the container. As an example, a container by default may
        enter via a `python` command, so if a Task runs a `script.py`, only args need to be set to `['script.py']`.
        See notes, for when running with emissary executor.
    env: Optional[List[Union[Env, BaseEnvFrom]]] = None
        The environment specifications to load. This operates on a single Enum that specifies whether to load the AWS
        credentials, or other available secrets.
    resources: Optional[Resources] = None
        A task resources configuration. See `hera.resources.Resources`.
    volumes: Optional[List[BaseVolume]] = None
        Any volumes to mount or create for the task. See `hera.volumes`.
    working_dir: Optional[str] = None
        The working directory to be set inside the executing container context.
    retry: Optional[RetryStrategy] = None
        A task retry strategy configuration. See `hera.retry_strategy.RetryStrategy`.
    tolerations: Optional[List[Toleration]] = None
        List of tolerations for the pod executing the task. This is used for scheduling purposes.
    node_selectors: Optional[Dict[str, str]] = None
        A collection of key value pairs that denote node selectors. This is used for scheduling purposes. If the task
        requires GPU resources, clients are encouraged to add a node selector for a node that can satisfy the
        requested resources. In addition, clients are encouraged to specify a GPU toleration, depending on the platform
        they submit the workflow to.
    labels: Optional[Dict[str, str]] = None
        A dictionary of labels to attach to the Task Template object metadata.
    annotations: Optional[Dict[str, str]] = None
        A dictionary of annotations to attach to the Task Template object metadata.
    security_context: Optional[TaskSecurityContext] = None
        Define security settings for the task container, overrides workflow security context.
    template_ref: Optional[TemplateRef] = None
        A template name reference to use with this task. Note that this is prioritized over a new template creation
        for each task definition.
    affinity: Optional[Affinity] = None
        The task affinity. This dictates the scheduling protocol of the pods running the task.
    memoize: Optional[Memoize] = None
        The memoize configuration for the task.
    pod_spec_patch: Optional[str] = None
        The fields of the task to patch, and how.
        See https://github.com/argoproj/argo-workflows/blob/master/examples/pod-spec-patch.yaml for an example.
    resource_template: Optional[ResourceTemplate]
        Resource template for managing Kubernetes resources. Resource template allows you to create, delete or update
        any type of Kubernetes resource, it accepts any kubectl action and valid K8S manifest.
    active_deadline_seconds: Optional[int]
        Optional duration in seconds relative to the task start time which the task
        is allowed to run.
    timeout: Optional[str]
        Set the total node execution timeout duration counting from the node's
        start time. This duration also includes time in which the node spends in Pending state.
    metrics: Optional[Union[Metric, List[Metric], Metrics]] = None
        Any built-in/custom Prometheus metrics to track.
    sidecars: Optional[List[Sidecar]] = None
        List of sidecars to create for the main pods of the container that runs the task.

    Notes
    -----
    When argo is using the emissary executor, the command must be set even when using args. See,
    https://argoproj.github.io/argo-workflows/workflow-executors/#emissary-emissary for how to get a containers
    entrypoint, inorder to set it as the command and to be able to set args on the Tasks.
    """

    def __init__(
        self,
        name: str,
        source: Optional[Union[Callable, str]] = None,
        with_param: Optional[Any] = None,
        with_sequence: Optional[Sequence] = None,
        inputs: Optional[
            Union[List[Union[Parameter, Artifact]], List[Union[Parameter, Artifact, Dict[str, Any]]], Dict[str, Any]]
        ] = None,
        outputs: Optional[List[Union[Parameter, Artifact]]] = None,
        dag: Optional[DAG] = None,
        image: Optional[str] = None,
        image_pull_policy: Optional[ImagePullPolicy] = None,
        daemon: bool = False,
        command: Optional[List[str]] = None,
        args: Optional[List[str]] = None,
        env: Optional[List[Union[Env, BaseEnvFrom]]] = None,
        resources: Optional[Resources] = None,
        volumes: Optional[List[_BaseVolume]] = None,
        working_dir: Optional[str] = None,
        retry_strategy: Optional[RetryStrategy] = None,
        tolerations: Optional[List[Toleration]] = None,
        node_selectors: Optional[Dict[str, str]] = None,
        labels: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None,
        security_context: Optional[TaskSecurityContext] = None,
        template_ref: Optional[TemplateRef] = None,
        affinity: Optional[Affinity] = None,
        memoize: Optional[Memoize] = None,
        pod_spec_patch: Optional[str] = None,
        resource_template: Optional[ResourceTemplate] = None,
        active_deadline_seconds: Optional[int] = None,
        timeout: Optional[str] = None,
        metrics: Optional[Union[Metric, List[Metric], Metrics]] = None,
        sidecars: Optional[List[Sidecar]] = None,
    ):
        if dag and source:
            raise ValueError("Cannot use both `dag` and `source`")
        if dag and template_ref:
            raise ValueError("Cannot use both `dag` and `template_ref`")
        if with_param is not None and with_sequence is not None:
            raise ValueError("Cannot use both `with_sequence` and `with_param`")
        self.name = validate_name(name)
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
        self.resource_template: Optional[ResourceTemplate] = resource_template
        self.active_deadline_seconds: Optional[int] = active_deadline_seconds
        self.timeout: Optional[str] = timeout
        self.metrics: Optional[Metrics] = None
        if metrics:
            if isinstance(metrics, Metric):
                self.metrics = Metrics([metrics])
            elif isinstance(metrics, list):
                assert all([isinstance(m, Metric) for m in metrics])
                self.metrics = Metrics(metrics)
            elif isinstance(metrics, Metrics):
                self.metrics = metrics
            else:
                raise ValueError(
                    "Unknown type provided for `metrics`, expected type is "
                    "`Optional[Union[Metric, List[Metric], Metrics]]`"
                )

        self.sidecars = sidecars
        self.image = image or GlobalConfig.image
        self.image_pull_policy = image_pull_policy
        self.daemon = daemon
        self.command = command
        self.args = args
        self.resources = resources
        self.working_dir = working_dir
        self.retry_strategy = retry_strategy
        self.tolerations = tolerations
        self.node_selector = node_selectors
        self.labels = labels or {}
        self.annotations = annotations or {}

        self.security_context = security_context
        self.template_ref = template_ref
        self.affinity = affinity

        self.exit_task: Optional[str] = None
        self.is_exit_task: bool = False
        self.depends: Optional[str] = None
        self.when: Optional[str] = None

        self.validate()

        # here we cast for otherwise `mypy` complains that Hera adds an incompatible type with a dictionary, which is
        # an acceptable type for the `inputs` field upon `init`
        self.inputs = cast(List[Union[Parameter, Artifact]], self.inputs)
        self.inputs += self._deduce_input_params()

        if hera.dag_context.is_set():
            hera.dag_context.add_task(self)

        for hook in GlobalConfig.task_post_init_hooks:
            hook(self)

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

    def next(self, other: "Task", operator: Operator = Operator.And, on: Optional[TaskResult] = None) -> "Task":
        """Sets this task as a dependency of the other passed task.

        Parameters
        ----------
        other: Task
            The other task to set a dependency for. The new dependency of the task is this task.

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

    def on_workflow_status(self, status: WorkflowStatus, op: Operator = Operator.Equals) -> "Task":
        """Execute this task conditionally on a workflow status."""
        expression = f"{{{{workflow.status}}}} {op} {status}"
        if self.when:
            self.when += f" {Operator.And} {expression}"
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

    def on_other_result(self, other: "Task", value: str, operator: Operator = Operator.Equals) -> "Task":
        """Execute this task based on the `other` result"""
        expression = f"'{other.get_result()}' {operator} {value}"
        if self.when:
            self.when += f" {Operator.And} {expression}"
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

    def _build_arguments(self) -> Optional[IoArgoprojWorkflowV1alpha1Arguments]:
        """Assembles and returns the task arguments"""
        parameters = [obj.as_argument() for obj in self.inputs if isinstance(obj, Parameter)]
        parameters = [p for p in parameters if p is not None]  # Some parameters might not resolve
        artifacts = [obj.as_argument() for obj in self.inputs if isinstance(obj, Artifact)]
        if len(parameters) + len(artifacts) == 0:
            # Some inputs do not require arguments (defaults)
            return None
        arguments = IoArgoprojWorkflowV1alpha1Arguments()
        if parameters:
            setattr(arguments, "parameters", parameters)
        if artifacts:
            setattr(arguments, "artifacts", artifacts)
        return arguments

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
                return Parameter(name, value, default=obj.default)
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
                return Artifact(name, path=obj.path, from_task=f"{{{{tasks.{self.name}.outputs.artifacts.{name}}}}}")
            raise NotImplementedError(type(obj))
        raise KeyError(f"No output artifact named `{name}` found")

    def get_result(self) -> str:
        """Returns the formatted field that points to the result/output of this task"""
        return f"{{{{tasks.{self.name}.outputs.result}}}}"

    def get_output_condition(self, operator: Operator, value: str) -> str:
        """Returns the output condition of the task based on the specified operator and value"""
        return f"{self.get_result()} {operator} {value}"

    def get_result_as(self, name: str) -> Parameter:
        return Parameter(name, value=f"{{{{tasks.{self.name}.outputs.result}}}}")

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
        if not self.args:
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
        inputs = [i.as_input() for i in self.inputs if isinstance(i, Parameter)]
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

    def _build_env(self) -> Tuple[List[EnvVar], List[EnvFromSource]]:
        """Assembles the environment variables for the task"""
        env = [e.build() for e in self.env if isinstance(e, Env)]
        env_from = [e.build() for e in self.env if isinstance(e, BaseEnvFrom)]
        return env, env_from

    def _build_container_kwargs(self) -> Dict:
        """Assemble the kwargs which will be used as a base for both script and container"""
        pull_policy = None
        if self.image_pull_policy:
            pull_policy = self.image_pull_policy.value

        env, env_from = self._build_env()

        kwargs = dict(
            image=self.image,
            image_pull_policy=pull_policy,
            command=self.get_command(),
            resources=self.resources.build() if self.resources else None,
            args=self.get_args(),
            env=env,
            env_from=env_from,
            working_dir=self.working_dir,
            volume_mounts=self._build_volume_mounts(),
            security_context=self.security_context.build() if self.security_context else None,
        )
        return {k: v for k, v in kwargs.items() if v}  # treats empty lists/None as false

    def _build_script(self) -> IoArgoprojWorkflowV1alpha1ScriptTemplate:
        """Assembles and returns the script template that contains the definition of the script to run in a task.

        Returns
        -------
        IoArgoprojWorkflowV1alpha1ScriptTemplate
            The script template representation of the task.
        """
        kwargs = self._build_container_kwargs()
        kwargs["source"] = self._get_script()
        template = IoArgoprojWorkflowV1alpha1ScriptTemplate(**kwargs)
        return template

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

    def _build_template(self) -> Optional[IoArgoprojWorkflowV1alpha1Template]:
        """Assembles and returns the template that contains the specification of the parameters, inputs, and other
        configuration required for the task be executed.

        Returns
        -------
        IoArgoprojWorkflowV1alpha1Template
            The template representation of the task.
        """
        if self.template_ref is not None:
            # Template already exists in cluster
            return None
        if self.dag is not None:
            return None
        template = IoArgoprojWorkflowV1alpha1Template(
            name=self.name,
        )

        if len(self.labels) + len(self.annotations) != 0:
            metadata = IoArgoprojWorkflowV1alpha1Metadata()
            if self.labels:
                setattr(metadata, "labels", self.labels)
            if self.annotations:
                setattr(metadata, "annotations", self.annotations)
            setattr(template, "metadata", metadata)

        built_inputs = self._build_inputs()
        built_outputs = self._build_outputs()
        built_tolerations = self._build_tolerations()

        if built_inputs is not None:
            setattr(template, "inputs", built_inputs)

        if built_outputs is not None:
            setattr(template, "outputs", built_outputs)

        if built_tolerations != []:
            setattr(template, "tolerations", built_tolerations)

        if self.daemon:
            setattr(template, "daemon", True)

        if self.node_selector is not None:
            setattr(template, "node_selector", self.node_selector)

        if self.retry_strategy is not None:
            setattr(template, "retry_strategy", self.retry_strategy.build())

        if self.source is not None:
            setattr(template, "script", self._build_script())
        elif self.resource_template is not None:
            setattr(template, "resource", self.resource_template.build())
        else:
            setattr(template, "container", self._build_container())

        affinity = self.affinity.build() if self.affinity else None
        if affinity is not None:
            setattr(template, "affinity", affinity)

        if self.memoize is not None:
            setattr(template, "memoize", self.memoize.build())

        if self.pod_spec_patch is not None:
            setattr(template, "podSpecPatch", self.pod_spec_patch)

        if self.active_deadline_seconds is not None:
            setattr(template, "active_deadline_seconds", str(self.active_deadline_seconds))

        if self.timeout is not None:
            setattr(template, "timeout", self.timeout)

        if self.metrics is not None:
            setattr(template, "metrics", self.metrics.build())

        if self.sidecars is not None:
            setattr(template, "sidecars", [sc.build() for sc in self.sidecars])

        return template

    def _build_tolerations(self) -> List[ArgoToleration]:
        """Assembles and returns the pod toleration objects required for scheduling a task.

        Returns
        -------
        Optional[List[_ArgoToleration]]
            The list of assembled tolerations.

        Notes
        -----
        If the task includes a GPU resource specification the client is responsible for specifying a GPU toleration.
        For GKE and Azure workloads `hera.toleration.GPUToleration` can be specified.
        """
        if self.tolerations is None:
            return []
        else:
            return [
                ArgoToleration(key=t.key, effect=t.effect, operator=t.operator, value=t.value)
                for t in self.tolerations
            ]

    def _build_dag_task(self) -> IoArgoprojWorkflowV1alpha1DAGTask:
        """Assembles and returns the graph task specification of the task.

        Returns
        -------
        V1alpha1DAGTask
            The graph task representation.
        """
        task = IoArgoprojWorkflowV1alpha1DAGTask(
            name=self.name,
            _check_type=False,
        )
        arguments = self._build_arguments()
        if arguments:
            setattr(task, "arguments", arguments)

        if self.exit_task:
            setattr(task, "on_exit", self.exit_task)

        if self.depends:
            setattr(task, "depends", self.depends)

        if self.when:
            setattr(task, "when", self.when)

        if self.template_ref is not None:
            setattr(task, "template_ref", self.template_ref.build())
        else:
            name = self.name if not self.dag else self.dag.name
            setattr(task, "template", name)

        if self.with_param:
            with_param = self.with_param
            if isinstance(with_param, Parameter):
                with_param = str(with_param)  # this will get the value
            elif not isinstance(self.with_param, str):
                with_param = json.dumps(self.with_param)
            setattr(task, "with_param", with_param)
        if self.with_sequence is not None:
            setattr(task, "with_sequence", self.with_sequence.build())

        return task
