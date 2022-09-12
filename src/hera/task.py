"""The implementation of a Hera task for Argo workflows"""

import copy
import inspect
import json
import textwrap
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union

from argo_workflows.model.env_from_source import EnvFromSource

if TYPE_CHECKING:
    from hera import DAG

from argo_workflows.models import (
    Container,
    EnvVar,
    IoArgoprojWorkflowV1alpha1Arguments,
    IoArgoprojWorkflowV1alpha1Backoff,
    IoArgoprojWorkflowV1alpha1DAGTask,
    IoArgoprojWorkflowV1alpha1Metadata,
    IoArgoprojWorkflowV1alpha1RetryStrategy,
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
from hera.env import EnvSpec
from hera.env_from import BaseEnvFromSpec
from hera.resource_template import ResourceTemplate
from hera.image import ImagePullPolicy
from hera.io import IO
from hera.memoize import Memoize
from hera.operator import Operator
from hera.parameter import Parameter
from hera.resources import Resources
from hera.retry import Retry
from hera.security_context import TaskSecurityContext
from hera.template_ref import TemplateRef
from hera.toleration import Toleration
from hera.validators import validate_name
from hera.volumes import (
    BaseVolume,
    EmptyDirVolume,
    ExistingVolume,
    SecretVolume,
    Volume,
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
    inputs: Optional[List[Union[Parameter, Artifact]]] = None
        `Input` or `Parameter` objects that hold parameter inputs. Note that while `InputFrom` is an accepted input
        parameter it cannot be used in conjunction with other types of inputs because of the dynamic aspect of the task
        creation process when provided with an `InputFrom`.
    outputs: Optional[List[Union[Parameter, Artifact]]] = None
        `Output` objects that dictate the outputs of the task.
    dag: Optional["DAG"] = None
        The DAG the task should execute.
    image: str = "python:3.7"
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
    env: Optional[List[Union[EnvSpec, BaseEnvFromSpec]]] = None
        The environment specifications to load. This operates on a single Enum that specifies whether to load the AWS
        credentials, or other available secrets.
    resources: Optional[Resources] = None
        A task resources configuration. See `hera.resources.Resources`.
    volumes: Optional[List[BaseVolume]] = None
        Any volumes to mount or create for the task. See `hera.volumes`.
    working_dir: Optional[str] = None
        The working directory to be set inside the executing container context.
    retry: Optional[Retry] = None
        A task retry configuration. See `hera.retry.Retry`.
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

    Notes
    ------
    When argo is using the emissary executor, the command must be set even when using args. See,
    https://argoproj.github.io/argo-workflows/workflow-executors/#emissary-emissary for how to get a containers
    entrypoint, inorder to set it as the command and to be able to set args on the Tasks.
    """

    def __init__(
        self,
        name: str,
        source: Optional[Union[Callable, str]] = None,
        with_param: Optional[Any] = None,
        inputs: Optional[List[Union[Parameter, Artifact]]] = None,
        outputs: Optional[List[Union[Parameter, Artifact]]] = None,
        dag: Optional["DAG"] = None,
        image: str = "python:3.7",
        image_pull_policy: Optional[ImagePullPolicy] = None,
        daemon: bool = False,
        command: Optional[List[str]] = None,
        args: Optional[List[str]] = None,
        env: Optional[List[Union[EnvSpec, BaseEnvFromSpec]]] = None,
        resources: Optional[Resources] = None,
        volumes: Optional[List[BaseVolume]] = None,
        working_dir: Optional[str] = None,
        retry: Optional[Retry] = None,
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
    ):
        if dag and source:
            raise ValueError("Cannot use both `dag` and `source`")
        if dag and template_ref:
            raise ValueError("Cannot use both `dag` and `template_ref`")
        self.name = validate_name(name)
        self.dag = dag
        self.source = source
        self.memoize = memoize
        self.volumes = volumes or []
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.env = env or []
        self.with_param = with_param
        self.inputs += self.deduce_parameters()
        self.pod_spec_patch = pod_spec_patch
        self.resource_template: Optional[ResourceTemplate] = resource_template

        self.image = image
        self.image_pull_policy = image_pull_policy
        self.daemon = daemon
        self.command = command
        self.args = args
        self.resources = resources
        self.working_dir = working_dir
        self.retry = retry
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

        if hera.dag_context.is_set():
            hera.dag_context.add_task(self)

    @property
    def ip(self):
        """Returns the specifications for the IP property of the task"""
        return f'"{{{{tasks.{self.name}.ip}}}}"'

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

        if not other.depends:
            # First dependency
            other.depends = self.name + condition
            return other
        elif self.name in other.depends:
            # TODO This is a bad check because self.name could be a subset of another name.
            # We can fix this with some proper string-splitting and elimination.
            raise ValueError(f"{self.name} already in {other.name}'s depends: {other.depends}")
        else:
            # Add follow-up dependency
            other.depends += f" {operator} {self.name + condition}"
        return other

    def __rshift__(self, other: "Task") -> "Task":
        """Sets this task as a dependency of the other passed task.

        Parameters
        ----------
        other: Task
            The other task(s) to set a dependency for. The new dependency of the task is this task.

        Returns
        -------
        Task
            The other task that was specified.

        Examples
        --------
        t1 = Task('t1')
        t2 = Task('t2')
        t1 >> t2  # this makes t2 execute AFTER t1
        """
        return self.next(other)

    def on_workflow_status(self, op: Operator, status: WorkflowStatus) -> "Task":
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

    def on_exit(self, other: "Task") -> "Task":
        """Execute `other` on completion (exit) of this Task."""
        self.exit_task = other.name
        other.is_exit_task = True
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

        See Also
        --------
        https://argoproj.github.io/argo-workflows/enhanced-depends-logic/
        """
        assert self.with_param is not None, "Can only use `when_all_succeeded` in combination with `with_param`"
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

        See Also
        --------
        https://argoproj.github.io/argo-workflows/enhanced-depends-logic/
        """
        assert self.with_param is not None, "Can only use `when_all_failed` in combination with `with_param`"
        return self.next(other, on=TaskResult.AllFailed)

    def validate(self):
        """
        Validates that the given function and corresponding params fit one another, raises AssertionError if
        conditions are not satisfied.
        """
        self._validate_io()
        if self.source:
            self._validate_source()
        if self.pod_spec_patch is not None:
            if not isinstance(self.pod_spec_patch, str):
                raise ValueError("`pod_spec_patch` must be `str` to handle argo expressions properly")

    def _validate_source(self):
        if isinstance(self.source, Callable):
            args = set(inspect.getfullargspec(self.source).args)
            if self.memoize:
                assert self.memoize.key in args, "memoize key must be a parameter of the function"

    def build_arguments(self) -> Optional[IoArgoprojWorkflowV1alpha1Arguments]:
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

    def get_outputs_as(self, name):
        """Gets all the output parameters from this task"""
        return Parameter(name=name, value=f"{{{{tasks.{self.name}.outputs.parameters}}}}")

    def get_output(
        self, name: str, path: Optional[str] = None, as_name: Optional[str] = None
    ) -> Union[Artifact, Parameter]:
        """Returns an output object in the form of an artifact or parameter based on the name.

        Parameters
        ----------
        name: str
            The name of the output

        Returns
        -------
        Union[Artifact, Parameter]
            The output object
        """
        if as_name is None:
            as_name = name
        obj = next((output for output in self.outputs if output.name == name), None)
        if obj:
            if isinstance(obj, Parameter):
                value = f"{{{{tasks.{self.name}.outputs.parameters.{name}}}}}"
                return Parameter(as_name, value, default=obj.default)
            if isinstance(obj, Artifact):
                if path is None:  # If a new path isn't set, we use the same as the origin
                    path = obj.path
                return Artifact(as_name, path=path, from_task=f"{{{{tasks.{self.name}.outputs.artifacts.{name}}}}}")
            raise NotImplementedError(type(obj))
        raise KeyError(f"No output named {name} found")

    def get_result(self) -> str:
        return f"{{{{tasks.{self.name}.outputs.result}}}}"

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

    def deduce_parameters(
        self,
    ) -> List[Parameter]:
        """Returns a list of Argo workflow parameters based on the function signature and the function parameters

        Returns
        -------
        Optional[str]
            A string representing the value which should be given to argos `with_params`
        """
        deduced_params: List[Parameter] = []
        if self.source and isinstance(self.source, Callable):
            # Source is a function
            signature = inspect.signature(self.source)
            arg_defaults = {}
            # if there are any kwargs arguments associated with the function signature, we set these as default values
            # for the argo defaults
            if list(signature.parameters.values()):
                for param in list(signature.parameters.values()):
                    if (
                        param.default != inspect.Parameter.empty
                        and param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
                    ):
                        arg_defaults[param.name] = param.default
                    else:
                        arg_defaults[param.name] = None

            non_default_args = [k for k, v in arg_defaults.items() if v is None]
            if not self.with_param:
                if len(non_default_args) == 0:
                    deduced_params += [Parameter(name=k, default=str(v)) for k, v in arg_defaults.items()]
                else:
                    missing_args = set(non_default_args) - set(
                        [p.name for p in self.inputs if isinstance(p, Parameter)]
                    )
                    deduced_params += [Parameter(name) for name in missing_args]

                    from hera.workflow_template import WorkflowTemplate

                    if missing_args and not isinstance(self, WorkflowTemplate):
                        # WorkflowTemplates do not know about arguments, so we allow this section to pass
                        raise ValueError(
                            "`with_params` is empty and there exists non-default arguments "
                            f"which aren't covered by `inputs`: {missing_args}"
                        )
            elif isinstance(self.with_param, str) or isinstance(self.with_param, Parameter):
                # with_param is a string-list or an argo reference (str) to something that resolves into a list.
                # We assume that each (resolved) object contains all arguments for function:
                unique_param_names = list(arg_defaults.keys())
                if len(unique_param_names) == 1:
                    deduced_params.append(Parameter(name=unique_param_names[0], value="{{item}}"))
                else:
                    for name in unique_param_names:
                        deduced_params.append(Parameter(name=name, value=f"{{{{item.{name}}}}}"))
            elif isinstance(self.with_param, list):
                unique_input_names = set()
                assert self.with_param is not None

                first_param = self.with_param[0]
                if not all(isinstance(x, type(first_param)) for x in self.with_param):
                    raise ValueError("Non-homogeneous types in `with_param`")

                # with_param should all be of the same type at this point
                with_param_holds_dicts = isinstance(first_param, dict)
                if with_param_holds_dicts:
                    for param in self.with_param:
                        missing_args = set(non_default_args) - param.keys()  # type: ignore
                        if missing_args:
                            raise ValueError(f"param in `with_params` misses non-default argument: {missing_args}")

                        unique_input_names.update(param.keys())  # type: ignore

                else:
                    if len(non_default_args) > 1:
                        raise ValueError(
                            f"source signature has multiple non-default arguments ({non_default_args})"
                            " which requires a dict-mapping in `with_param`"
                        )
                    # Add the exclusive non-default argument
                    unique_input_names.add(non_default_args[0])

                # We need to make sure these args are provided in `with_param`
                missing_args = set(non_default_args) - set(unique_input_names)
                if missing_args:
                    raise ValueError(
                        f"Incomplete argument mapping between function and `with_params`: {missing_args}`"
                    )

                if with_param_holds_dicts:
                    for param_name in unique_input_names:
                        value = f"{{{{item.{param_name}}}}}"
                        deduced_params.append(Parameter(name=param_name, value=value))
                else:
                    # Function has only one mandatory argument
                    main_param_name = list(unique_input_names)[0]
                    deduced_params.append(Parameter(name=main_param_name, value="{{item}}"))

                # Add default arguments
                for param_name in arg_defaults.keys() - unique_input_names:
                    deduced_params.append(Parameter(name=param_name, value=str(arg_defaults.get(param_name))))
            else:
                raise NotImplementedError(f"Type {type(self.with_param)} not supported for `with_param`")

        elif self.dag:
            if self.dag.inputs:
                if len(self.dag.inputs) == 1:
                    deduced_params.append(Parameter(name=self.dag.inputs[0].name, value="{{item}}"))
                else:
                    for p in self.dag.inputs:
                        deduced_params.append(Parameter(name=p.name, value=f"{{{{item.{p.name}}}}}"))

        if self.with_param and not deduced_params and not self.inputs:
            raise ValueError(
                "`inputs` is empty, and no input parameters could be deduced from `source` and `with_params`"
            )

        for spec in self.env:
            if isinstance(spec, EnvSpec) and spec.value_from_input:
                deduced_params.append(Parameter(name=spec.name, value=spec.value_from_input))

        return deduced_params  # type: ignore

    def get_param_script_portion(self) -> Optional[str]:
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

    def get_script(self) -> str:
        """Assembles and returns a script representation of the given function, along with the extra script material
        prefixed to the string. The script is expected to be a callable function the client is interested in submitting
        for execution on Argo and the script_extra material represents the parameter loading part obtained, likely,
        through get_param_script_portion.

        Returns
        -------
        str
            Final formatted script.
        """
        if isinstance(self.source, Callable):
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

                script_extra = self.get_param_script_portion() if args else None
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

    def build_volume_mounts(self) -> Optional[List[VolumeMount]]:
        """Assembles the list of volumes to be mounted by the task.

        Returns
        -------
        List[VolumeMount]
            The list of volume mounts to be added to the task specification.
        """
        return [v.build_mount() for v in self.volumes]

    def build_volume_claim_templates(self) -> Optional[List[PersistentVolumeClaim]]:
        """Assembles the list of volume claim templates to be created for the task."""
        return [v.build_claim_spec() for v in self.volumes if isinstance(v, Volume)]

    def build_persistent_volume_claims(self) -> Optional[List[ArgoVolume]]:
        """Assembles the list of Argo volume specifications"""
        return [
            v.build_claim_spec()
            for v in self.volumes
            if isinstance(v, ExistingVolume) or isinstance(v, SecretVolume) or isinstance(v, EmptyDirVolume)
        ]

    def build_env(self) -> Tuple[List[EnvVar], List[EnvFromSource]]:
        """Assembles the environment variables for the task"""
        env = [e.build() for e in self.env if isinstance(e, EnvSpec)]
        env_from = [e.build() for e in self.env if isinstance(e, BaseEnvFromSpec)]
        return env, env_from

    def _build_container_kwargs(self) -> Dict:
        """Assemble the kwargs which will be used as a base for both script and container"""
        pull_policy = None
        if self.image_pull_policy:
            pull_policy = self.image_pull_policy.value

        env, env_from = self.build_env()

        kwargs = dict(
            image=self.image,
            image_pull_policy=pull_policy,
            command=self.get_command(),
            resources=self.resources.build() if self.resources else None,
            args=self.get_args(),
            env=env,
            env_from=env_from,
            working_dir=self.working_dir,
            volume_mounts=self.build_volume_mounts(),
            security_context=self.security_context.build_security_context() if self.security_context else None,
        )
        return {k: v for k, v in kwargs.items() if v}  # treats empty lists/None as false

    def build_script(self) -> IoArgoprojWorkflowV1alpha1ScriptTemplate:
        """Assembles and returns the script template that contains the definition of the script to run in a task.

        Returns
        -------
        IoArgoprojWorkflowV1alpha1ScriptTemplate
            The script template representation of the task.
        """
        kwargs = self._build_container_kwargs()
        kwargs["source"] = self.get_script()
        template = IoArgoprojWorkflowV1alpha1ScriptTemplate(**kwargs)
        return template

    def build_container(self) -> Container:
        """Assembles and returns the container for the task to run in.

        Returns
        -------
        Container
            The container template representation of the task.
        """
        container_args = self._build_container_kwargs()
        container = Container(**container_args)
        return container

    def build_template(self) -> Optional[IoArgoprojWorkflowV1alpha1Template]:
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

        built_inputs = self.build_inputs()
        built_outputs = self.build_outputs()
        built_tolerations = self.build_tolerations()

        if built_inputs is not None:
            setattr(template, "inputs", built_inputs)

        if built_outputs is not None:
            setattr(template, "outputs", built_outputs)

        if built_tolerations is not None:
            setattr(template, "tolerations", built_tolerations)

        if self.daemon:
            setattr(template, "daemon", True)

        if self.node_selector is not None:
            setattr(template, "node_selector", self.node_selector)

        retry_strategy = self.build_retry_strategy()
        if retry_strategy is not None:
            setattr(template, "retry_strategy", retry_strategy)

        if self.source is not None:
            setattr(template, "script", self.build_script())
        else:
            setattr(template, "container", self.build_container())

        affinity = self.affinity.get_spec() if self.affinity else None
        if affinity is not None:
            setattr(template, "affinity", affinity)

        if self.memoize is not None:
            setattr(template, "memoize", self.memoize.build())

        if self.pod_spec_patch is not None:
            setattr(template, "podSpecPatch", self.pod_spec_patch)

        if self.resource_template is not None:
            setattr(template, "resource", self.resource_template.build())

        return template

    def build_retry_strategy(self) -> Optional[IoArgoprojWorkflowV1alpha1RetryStrategy]:
        """Assembles and returns a retry strategy for the task. This is dictated by the task `retry_limit`.

        Returns
        -------
        Optional[IoArgoprojWorkflowV1alpha1RetryStrategy]
            A V1alpha1RetryStrategy object if `retry_limit` is specified, None otherwise.
        """
        if self.retry:
            strategy = IoArgoprojWorkflowV1alpha1RetryStrategy()
            if self.retry.duration is not None and self.retry.max_duration is not None:
                setattr(
                    strategy,
                    "backoff",
                    IoArgoprojWorkflowV1alpha1Backoff(
                        duration=str(self.retry.duration), max_duration=str(self.retry.max_duration)
                    ),
                )
            if self.retry.limit is not None:
                setattr(strategy, "limit", str(self.retry.limit))
            if self.retry.retry_policy is not None:
                setattr(strategy, "retry_policy", str(self.retry.retry_policy.value))

            return strategy
        return None

    def build_tolerations(self) -> List[ArgoToleration]:
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

    def build_dag_task(self) -> IoArgoprojWorkflowV1alpha1DAGTask:
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
        arguments = self.build_arguments()
        if arguments:
            setattr(task, "arguments", arguments)

        if self.exit_task:
            setattr(task, "on_exit", self.exit_task)

        if self.depends:
            setattr(task, "depends", self.depends)

        if self.when:
            setattr(task, "when", self.when)

        if self.template_ref:
            setattr(task, "template_ref", self.template_ref.build_spec)
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
        return task
