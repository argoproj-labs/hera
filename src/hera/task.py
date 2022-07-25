"""The implementation of a Hera task for Argo workflows"""

import copy
import inspect
import json
import textwrap
from typing import Callable, Dict, List, Optional, Union

from argo_workflows.models import (
    Container,
    EnvFromSource,
    EnvVar,
    IoArgoprojWorkflowV1alpha1Arguments,
    IoArgoprojWorkflowV1alpha1Artifact,
    IoArgoprojWorkflowV1alpha1Backoff,
    IoArgoprojWorkflowV1alpha1ContinueOn,
    IoArgoprojWorkflowV1alpha1DAGTask,
    IoArgoprojWorkflowV1alpha1Inputs,
    IoArgoprojWorkflowV1alpha1LifecycleHook,
    IoArgoprojWorkflowV1alpha1Metadata,
    IoArgoprojWorkflowV1alpha1Outputs,
    IoArgoprojWorkflowV1alpha1Parameter,
    IoArgoprojWorkflowV1alpha1RetryStrategy,
    IoArgoprojWorkflowV1alpha1ScriptTemplate,
    IoArgoprojWorkflowV1alpha1Template,
    ResourceRequirements,
    SecurityContext,
)
from argo_workflows.models import Toleration as ArgoToleration
from argo_workflows.models import VolumeMount

import hera
from hera.affinity import Affinity
from hera.artifact import Artifact
from hera.env import EnvSpec
from hera.env_from import BaseEnvFromSpec
from hera.image import ImagePullPolicy
from hera.memoize import Memoize
from hera.operator import Operator
from hera.parameter import Parameter
from hera.resources import Resources
from hera.retry import Retry
from hera.security_context import TaskSecurityContext
from hera.template_ref import TemplateRef
from hera.toleration import Toleration
from hera.workflow_status import WorkflowStatus


class Task:
    """An Argo task representation. This is used to submit functions to be executed on Argo.

    The task can take a function, along with its parameters, resource configuration, a volume, etc, and submit it for
    remote execution.

    Parameters
    ----------
    name: str
        The name of the task to submit as part of a workflow.
    func: Optional[Callable]
        The function to execute remotely.
    func_params: Optional[List[Dict[str, Union[int, str, float, dict, BaseModel]]]] = None
        The parameters of the function to execute. Note that this works together with parallel. If the params are
        constructed using a single list of values and parallel is False, it is going to be interpreted as a single
        function call with the given parameters. Otherwise, if parallel is False and the list of params is a list of
        lists (each list contains a series of values to pass to the function), the the task will execute as a task
        group and schedule multiple function calls in parallel.
    input_from: Optional[InputFrom] = None
        An InputFrom object that denotes the task this will receive input from. The other task results are read in via
        parameters. The parameter specifications follow the ones specified by InputFrom i.e the names of the parameters
        that are set.
    inputs: Optional[List[Input]] = None
        `Input` objects that hold parameter inputs. Note that while `InputFrom` is an accepted input
        parameter it cannot be used in conjunction with other types of inputs because of the dynamic aspect of the task
        creation process when provided with an `InputFrom`.
    outputs: Optional[List[Output]] = None
        `Output` objects that dictate the outputs of the task.
    image: str = 'python:3.7'
        The image to use in the execution of the function.
    image_pull_policy: ImagePullPolicy = 'Always'
        The image_pull_policy represents the way to tell Kubernetes if your Task needs to pull and image or not.
        In case of local development/testing this can be set to 'Never'.
    daemon: Optional[bool] = None
        Whether to run the task as a daemon.
    command: Optional[List[str]] = None
        The command to use in the environment where the function runs in order to run the specific function. Note that
        the specified function is parsed, stored as a string, and ultimately placed in a separate file inside the task
        and invoked via `python script_file.py`. Also note, that when neither command nor args are set, the command
        will default to python. This command offers users the opportunity to start up the script in a different way
        e.g `time python` to time execution, `horovodrun -p X` to use horovod from an image that allows training models
        on multiple GPUs, etc.
    args: Optionals[List[str]] = None
        Optional list of arguments to run in the container. This can be used as an alternative to command, with the
        advantage of not overriding the set entrypoint of the container. As an example, a container by default may
        enter via a `python` command, so if a Task runs a `script.py`, only args need to be set to `['script.py']`.
        See notes, for when running with emissary executor.
    env_specs: Optional[List[EnvSpec]] = None
        The environment specifications to load. This operates on a single Enum that specifies whether to load the AWS
        credentials, or other available secrets.
    env_from_specs: Optional[List[BaseEnvFromSpec]] = None
        The environment specifications to load from ConfigMap or Secret.
    resources: Resources = Resources()
        A task resources configuration. See `hera.v1.resources.Resources`.
    working_dir: Optional[str] = None
        The working directory to be set inside the executing container context.
    retry: Optional[Retry] = None
        A task retry configuration. See `hera.v1.retry.Retry`.
    tolerations: Optional[List[Toleration]] = None
        List of tolerations for the pod executing the task. This is used for scheduling purposes.
    node_selectors: Optional[Dict[str, str]] = None
        A collection of key value pairs that denote node selectors. This is used for scheduling purposes. If the task
        requires GPU resources, clients are encouraged to add a node selector for a node that can satisfy the
        requested resources. In addition, clients are encouraged to specify a GPU toleration, depending on the platform
        they submit the workflow to.
    labels: Optional[Dict[str, str]] = None
        A Dict of labels to attach to the Task Template object metadata.
    annotations: Optional[Dict[str, str]] = None
        A Dict of annotations to attach to the Task Template object metadata.
    security_context: Optional[TaskSecurityContext] = None
        Define security settings for the task container, overrides workflow security context.
    continue_on_fail: bool = False
        Whether to continue task chain execution when this task fails.
    continue_on_error: bool = False
        Whether to continue task chain execution this task errors.
    template_ref: Optional[TemplateRef] = None
        A template name reference to use with this task. Note that this is prioritized over a new template creation
        for each task definition.
    affinity: Optional[Affinity] = None
        The task affinity. This dictates the scheduling protocol of the pods running the task.
    memoize: Optional[Memoize] = None
        The memoize configuration for the task.

    Notes
    ------
    When argo is using the emissary executor, the command must be set even when using args. See,
    https://argoproj.github.io/argo-workflows/workflow-executors/#emissary-emissary for how to get a containers
    entrypoint, inorder to set it as the command and to be able to set args on the Tasks.
    """

    def __init__(
        self,
        name: str,
        func: Optional[Callable] = None,
        with_param: Optional[Union[List[Dict[str, Union[int, str, float, dict]]], List[str], str]] = None,
        inputs: Optional[List[Union[Parameter, Artifact]]] = None,
        outputs: Optional[List[Union[Parameter, Artifact]]] = None,
        image: str = "python:3.7",
        image_pull_policy: Optional[ImagePullPolicy] = ImagePullPolicy.Always,
        daemon: bool = False,
        command: Optional[List[str]] = None,
        args: Optional[List[str]] = None,
        env: Optional[List[Union[EnvSpec, BaseEnvFromSpec]]] = None,
        resources: Resources = Resources(),
        working_dir: Optional[str] = None,
        retry: Optional[Retry] = None,
        tolerations: Optional[List[Toleration]] = None,
        node_selectors: Optional[Dict[str, str]] = None,
        labels: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None,
        security_context: Optional[TaskSecurityContext] = None,
        continue_on_fail: Optional[bool] = None,
        continue_on_error: Optional[bool] = None,
        template_ref: Optional[TemplateRef] = None,
        affinity: Optional[Affinity] = None,
        memoize: Optional[Memoize] = None,
    ):
        # Some of these methods have side-effects*
        self.name = name.replace("_", "-")  # RFC1123
        self.func = func
        self.memoize = memoize
        self.inputs = inputs or []
        self.with_param = self.deduce_inputs(with_param)  # self.inputs*
        self.outputs = outputs or []
        self.env = self.get_env(env)  # self.inputs*
        self.env_from = self.get_env_from_source(env)
        self.validate()

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
        self.continue_on_fail = continue_on_fail
        self.continue_on_error = continue_on_error
        self.template_ref = template_ref
        self.affinity = affinity
        self.exit_task: Optional[Task] = None

        self.argo_parameters = self.get_parameters()
        self.argo_arguments = self.assemble_arguments()
        self.argo_inputs = self.assemble_inputs()
        self.argo_outputs = self.assemble_outputs()
        self.argo_resources = self.assemble_resources()
        self.argo_template = self.assemble_task_template()
        self.argo_task = self.get_spec()

        if hera.context.is_set():
            hera.context.add_task(self)

    @property
    def ip(self):
        return f'"{{{{tasks.{self.name}.ip}}}}"'

    def next(self, other: "Task") -> "Task":
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

        if hasattr(other.argo_task, "depends"):
            if self.argo_task.name in other.argo_task.depends:
                return other
            other.argo_task.depends += f" && {self.argo_task.name}"
            return other

        if not hasattr(other.argo_task, "dependencies"):
            setattr(other.argo_task, "dependencies", [self.argo_task.name])
        else:
            if self.argo_task.name in other.argo_task.dependencies:
                # already a dependency
                return other
            other.argo_task.dependencies.append(self.argo_task.name)
        return other

    def __rshift__(self, other: "Task") -> "Task":
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
        t1 = Task('t1')
        t2 = Task('t2')
        t1 >> t2  # this makes t2 execute AFTER t1
        """
        return self.next(other)

    def when(self, other: "Task", operator: Operator, value: str) -> "Task":
        """Sets this task as a dependency of the other passed task if the condition match.

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
        t2.when(t1, Operator.equals, "t2")
        t3.when(t1, Operator.equals, "t3")
        """
        self.argo_task.when = f"{{{{tasks.{other.name}.outputs.result}}}} {operator.value} {value}"
        return other.next(self)

    def on_workflow_status(self, op: Operator, status: WorkflowStatus) -> "Task":
        """Execute this task conditionally on a workflow status."""
        self.argo_task.when = f"{{{{workflow.status}}}} {op.value} {status.value}"
        return self

    def on_success(self, other: "Task") -> "Task":
        """Execute `other` when this task succeeds"""
        other.argo_task.when = f"{{{{tasks.{self.name}.status}}}} {Operator.equals.value} Succeeded"
        return self.next(other)

    def on_failure(self, other: "Task") -> "Task":
        """Execute `other` when this task fails. This forces `continue_on_fail` to be True"""
        self.continue_on_fail = True
        if hasattr(self.argo_task, "continue_on"):
            continue_on: IoArgoprojWorkflowV1alpha1ContinueOn = getattr(self.argo_task, "continue_on")
            setattr(continue_on, "failed", True)
            setattr(self.argo_task, "continue_on", continue_on)
        else:
            setattr(self.argo_task, "continue_on", self.get_continue_on())

        other.argo_task.when = f"{{{{tasks.{self.name}.status}}}} {Operator.equals.value} Failed"
        return self.next(other)

    def on_error(self, other: "Task") -> "Task":
        """Execute `other` when this task errors. This forces `continue_on_error` to be True"""
        self.continue_on_error = True
        if hasattr(self.argo_task, "continue_on"):
            continue_on: IoArgoprojWorkflowV1alpha1ContinueOn = getattr(self.argo_task, "continue_on")
            setattr(continue_on, "error", True)
            setattr(self.argo_task, "continue_on", continue_on)
        else:
            setattr(self.argo_task, "continue_on", self.get_continue_on())

        other.argo_task.when = f"{{{{tasks.{self.name}.status}}}} {Operator.equals.value} Error"
        return self.next(other)

    def on_exit(self, other: "Task") -> "Task":
        """Execute `other` on completion (exit) of this Task."""
        self.exit_task = other
        exit_hook = {"exit": IoArgoprojWorkflowV1alpha1LifecycleHook(template=other.argo_template.name)}
        setattr(self.argo_task, "hooks", exit_hook)
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
        # assert hasattr(self.argo_task, "with_items") or self.input_from is not None, (
        #     "Can only use `when_any_succeeded` for tasks with more than 1 item, which happens "
        #     "with multiple `func_params or setting `input_from`"
        # )
        assert (
            not other.continue_on_fail and not other.continue_on_error
        ), "The use of `when_any_succeeded` is incompatible with setting `continue_on_error/fail`"

        if hasattr(other.argo_task, "depends"):
            depends = other.argo_task.depends
        elif hasattr(other.argo_task, "dependencies"):
            depends = _dependencies_to_depends(other.argo_task.dependencies)
        else:
            depends = ""

        if f"{self.name}.AnySucceeded" in depends:
            return self

        if depends:
            depends += f" && {self.name}.AnySucceeded"
        else:
            depends = f"{self.name}.AnySucceeded"

        if hasattr(other.argo_task, "dependencies"):
            # calling delattr(other.argo_task, 'dependencies') results in AttributeError
            # so recreate the argo task field
            self.argo_task = self.get_spec()
        setattr(other.argo_task, "depends", depends)

        return self

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
        # assert hasattr(self.argo_task, "with_items") or self.input_from is not None, (
        #     "Can only use `when_all_failed` for tasks with more than 1 item, which happens "
        #     "with multiple `func_params or setting `input_from`"
        # )
        assert (
            not other.continue_on_fail and not other.continue_on_error
        ), "The use of `when_all_failed` is incompatible with setting `continue_on_error/fail`"

        if hasattr(other.argo_task, "depends"):
            depends = other.argo_task.depends
        elif hasattr(other.argo_task, "dependencies"):
            depends = _dependencies_to_depends(other.argo_task.dependencies)
        else:
            depends = ""

        if f"{self.name}.AllFailed" in depends:
            return self

        if depends:
            depends += f" && {self.name}.AllFailed"
        else:
            depends = f"{self.name}.AllFailed"

        if hasattr(other.argo_task, "dependencies"):
            # calling delattr(other.argo_task, 'dependencies') results in AttributeError
            # so recreate the argo task field
            self.argo_task = self.get_spec()
        setattr(other.argo_task, "depends", depends)

        return self

    def validate(self):
        """
        Validates that the given function and corresponding params fit one another, raises AssertionError if
        conditions are not satisfied.
        """
        # verify artifacts are uniquely names
        # if self.input_artifacts:
        #     assert len(set([i.name for i in self.input_artifacts])) == len(
        #         self.input_artifacts
        #     ), "input artifact names must be unique"
        # if self.output_artifacts:
        #     assert len(set([i.name for i in self.output_artifacts])) == len(
        #         self.output_artifacts
        #     ), "output artifact names must be unique"
        if self.inputs:
            assert len(set([i.name for i in self.inputs])) == len(self.inputs), "input parameters must be unique"
        if self.outputs:
            assert len(set([o.name for o in self.outputs])) == len(self.outputs), "output parameters must be unique"

        if self.func:
            self._validate_func()

    def _validate_func(self):
        args = set(inspect.getfullargspec(self.func).args)
        # if args:
        #     if self.inputs:
        #         assert args.issuperset(
        #             set([i.name for i in self.inputs])
        #         ), "function parameters must intersect with at least one `Input` when `inputs` is specified"
        #     else:
        #         signature = inspect.signature(self.func)
        #         keywords = []

        #         if list(signature.parameters.values()):
        #             for param in list(signature.parameters.values()):
        #                 if (
        #                     param.default != inspect.Parameter.empty
        #                     and param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
        #                 ):
        #                     keywords.append(param.name)
        #         if len(keywords) == len(args):
        #             pass  # these are all kwargs, safe to skip
        #         else:
        #             # otherwise, it must be the case that the client passes func_params
        #             assert self.with_param, "no parameters passed for function"

        if self.memoize:
            assert self.memoize.key in args, "memoize key must be a parameter of the function"

    # if self.func_params:
    #     for params in self.func_params:
    #         if isinstance(params, BaseModel):
    #             params = params.dict()
    #         assert args.issuperset(set(params.keys())), "mismatched function arguments and passed parameters"

    def assemble_arguments(self) -> IoArgoprojWorkflowV1alpha1Arguments:
        """Assembles and returns the task arguments"""
        return IoArgoprojWorkflowV1alpha1Arguments(
            parameters=[obj.as_argument() for obj in self.inputs if isinstance(obj, Parameter)],
            artifacts=[obj.as_argument() for obj in self.inputs if isinstance(obj, Artifact)],
        )

    def assemble_inputs(self) -> IoArgoprojWorkflowV1alpha1Inputs:
        """Assembles the inputs of the task."""
        return IoArgoprojWorkflowV1alpha1Inputs(
            parameters=[obj.as_input() for obj in self.inputs if isinstance(obj, Parameter)],
            artifacts=[obj.as_input() for obj in self.inputs if isinstance(obj, Artifact)],
        )

    def assemble_outputs(self) -> IoArgoprojWorkflowV1alpha1Outputs:
        """Assembles and returns the task outputs"""
        return IoArgoprojWorkflowV1alpha1Outputs(
            parameters=[obj.as_output() for obj in self.outputs if isinstance(obj, Parameter)],
            artifacts=[obj.as_output() for obj in self.outputs if isinstance(obj, Artifact)],
        )

    def get_outputs_as(self, name):
        """Gets all the output parameters from this task"""
        return Parameter(name=name, value=f"{{{{tasks.{self.name}.outputs.parameters}}}}")

    def get_output(
        self, name: str, path: Optional[str] = None, as_name: Optional[str] = None
    ) -> Union[Artifact, Parameter]:
        if as_name is None:
            as_name = name
        obj = next(output for output in self.outputs if output.name == name)
        if isinstance(obj, Parameter):
            return Parameter(as_name, value=f"{{{{tasks.{self.name}.outputs.parameters.{name}}}}}")
        elif isinstance(obj, Artifact):
            if path is None:
                raise ValueError(f"Output with name `{name}` is of type `Artifact` which requires a `path` argument")
            return Artifact(as_name, path=path, from_task=f"{{{{tasks.{self.name}.outputs.artifacts.{name}}}}}")
        else:
            raise NotImplementedError()

    def get_result(self) -> str:
        return f"{{{{tasks.{self.name}.outputs.result}}}}"

    def get_result_as(self, name: str) -> Parameter:
        return Parameter(name, value=f"{{{{tasks.{self.name}.outputs.result}}}}")

    def get_command(self) -> Optional[List[str]]:
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
        if not self.args:
            return None
        return [str(arg) for arg in self.args]

    def get_env(self, specs: Optional[List[Union[EnvSpec, BaseEnvFromSpec]]]) -> List[EnvVar]:
        """Returns a list of Argo workflow environment variables based on the specified Hera environment specifications.

        Parameters
        ----------
        specs: Optional[List[EnvSpec]]
            Hera environment specifications.

        Returns
        -------
        List[EnvVar]
            A list of Argo environment specifications, if any specs are provided.
        """
        env_vars: List[EnvVar] = []
        env_specs: List[EnvSpec] = [s for s in specs or [] if isinstance(s, EnvSpec)]
        for spec in env_specs:
            if spec.value_from_input:
                self.inputs.append(Parameter(name=spec.name, value=spec.value_from_input))
            env_vars.append(spec.argo_spec)
        return env_vars

    def get_env_from_source(self, specs: Optional[List[Union[EnvSpec, BaseEnvFromSpec]]]) -> List[EnvFromSource]:
        """Returns a list of Argo environment variables based on the Hera environment from source specifications.

        Parameters
        ----------
        Optional[List[BaseEnvFromSpec]]
            Hera environment from specifications.

        Returns
        -------
        List[EnvFromSource]
            A list of env variables from specified sources.
        """
        base_env_specs: List[BaseEnvFromSpec] = [s for s in specs or [] if isinstance(s, BaseEnvFromSpec)]
        return [s.argo_spec for s in base_env_specs]

    def get_parameters(self) -> List[Union[IoArgoprojWorkflowV1alpha1Parameter, IoArgoprojWorkflowV1alpha1Artifact]]:
        """Returns a list of Argo workflow task parameters based on the inputs.

        Returns
        -------
        List[IoArgoprojWorkflowV1alpha1Parameter]
            The list of constructed Argo parameters.

        """
        return [i.as_argument() for i in self.inputs]

    def deduce_inputs(self, with_param) -> Optional[str]:
        """Returns a list of Argo workflow parameters based on the function signature and the function parameters

        Returns
        -------
        List[Parameter]
            The list of constructed Argo parameters.
        """
        parameters: List[Parameter] = []
        if self.func:
            signature = inspect.signature(self.func)
            arg_defaults = {}
            # if there are any keyword arguments associated with the function signature, we set them as default values
            # so Argo passes them in
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

            if with_param is None:
                if len(non_default_args) == 0:
                    parameters += [Parameter(name=k, value=v) for k, v in arg_defaults.items()]
                else:
                    missing_args = set(non_default_args) - set(
                        [p.name for p in self.inputs if isinstance(p, Parameter)]
                    )
                    if missing_args:
                        raise ValueError(
                            f"`with_params` is empty and there exists non-default arguments which aren't covered by `inputs`: {missing_args}"
                        )
            elif isinstance(with_param, str):
                # Pure string or string-reference from another task.
                # We assume that each object contains all arguments for function:
                unique_param_names = list(arg_defaults.keys())
                if len(unique_param_names) == 1:
                    parameters.append(Parameter(name=unique_param_names[0], value="{{item}}"))
                else:
                    for name in unique_param_names:
                        parameters.append(Parameter(name=name, value=f"{{{{item.{name}}}}}"))
            else:
                unique_input_names = set()
                # with_param assumed to be a dictionary
                assert with_param is not None

                first_type = type(with_param[0])
                if not all((type(x) is first_type) for x in with_param):
                    raise ValueError("Non-homogeneous types in `with_param`")

                # with_params should all be of the same type at this point
                with_param_is_dicts = isinstance(with_param[0], dict)
                if with_param_is_dicts:
                    for param in with_param:
                        unique_input_names.update(param.keys())
                else:
                    if len(non_default_args) > 1:
                        raise ValueError(
                            f"function signature has multiple non-default arguments ({non_default_args})"
                            " which requires a dict-mapping in `with_param`"
                        )
                    else:
                        # Add the exclusive non-default argument
                        unique_input_names.add(non_default_args[0])

                # We need to make sure these args are provided in `with_param`
                missing_args = set(non_default_args) - set(unique_input_names)
                if missing_args:
                    raise ValueError(
                        f"Incomplete argument mapping between function and `with_params`: {missing_args}`"
                    )

                if with_param_is_dicts:
                    for param_name in unique_input_names:
                        parameters.append(Parameter(name=param_name, value=f"{{{{item.{param_name}}}}}"))
                else:
                    # Function has only one mandatory argument
                    main_param_name = list(unique_input_names)[0]
                    parameters.append(Parameter(name=main_param_name, value="{{item}}"))

                # Add default arguments
                for param_name in arg_defaults.keys() - unique_input_names:
                    parameters.append(Parameter(name=param_name, value=arg_defaults.get(param_name)))

        # Add all accumulated parameters to inputs
        for p in parameters:
            self.inputs.append(p)

        # self.with_param should always be Optional[str]
        # if len(parameters) > 0 and with_param is not None and not isinstance(with_param, str):
        if with_param and not isinstance(with_param, str):
            with_param = json.dumps(with_param)

        return with_param

    def get_param_script_portion(self) -> str:
        """Constructs and returns a script that loads the parameters of the specified arguments. Since Argo passes
        parameters through {{input.parameters.name}} it can be very cumbersome for users to manage that. This creates a
        script that automatically imports json and loads/adds code to interpret each independent argument into the
        script.

        Returns
        -------
        str
            The string representation of the script to load.
        """
        extract = "import json\n"
        for param in self.argo_parameters:
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
        script = ""
        script_extra = self.get_param_script_portion() if inspect.getfullargspec(self.func).args else None
        if script_extra:
            script = copy.deepcopy(script_extra)
            script += "\n"

        # content represents the function components, separated by new lines
        # therefore, the actual code block occurs after the end parenthesis, which is a literal `):\n`
        content = inspect.getsourcelines(self.func)[0]
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

    def assemble_resources(self) -> ResourceRequirements:
        """Assembles an Argo resource requirements object with the given resource configuration.

        Returns
        -------
        ResourceRequirements
            A configured Argo resource requirement with the given configuration.
        """
        max_cpu = self.resources.max_cpu is not None
        max_mem = self.resources.max_mem is not None
        max_custom = self.resources.max_custom_resources is not None

        resource = ResourceRequirements(
            requests={
                "cpu": str(self.resources.min_cpu),
                "memory": self.resources.min_mem,
            },
            limits={
                "cpu": str(self.resources.max_cpu) if max_cpu else str(self.resources.min_cpu),
                "memory": self.resources.max_mem if max_mem else self.resources.min_mem,
            },
        )

        if self.resources.min_custom_resources is not None:
            resource.requests.update(**self.resources.min_custom_resources)

        if max_custom:
            resource.limits.update(**self.resources.max_custom_resources)
        elif self.resources.min_custom_resources:
            resource.limits.update(**self.resources.min_custom_resources)

        if self.resources.gpus:
            resource.requests["nvidia.com/gpu"] = str(self.resources.gpus)
            resource.limits["nvidia.com/gpu"] = str(self.resources.gpus)
        return resource

    def get_volume_mounts(self) -> List[VolumeMount]:
        """Assembles the list of volumes to be mounted by the task.

        Returns
        -------
        List[VolumeMount]
            The list of volume mounts to be added to the task specification.
        """
        volumes = []
        if self.resources.volumes:
            for volume in self.resources.volumes:
                volumes.append(volume.get_mount())
        return volumes

    def get_script_def(self) -> Optional[IoArgoprojWorkflowV1alpha1ScriptTemplate]:
        """Assembles and returns the script template that contains the definition of the script to run in a task.

        Returns
        -------
        Optional[IoArgoprojWorkflowV1alpha1ScriptTemplate]
            The script template representation of the task.
        """
        if self.func is None:
            return None

        script_kwargs = {
            "name": self.name,
            "image": self.image,
            "image_pull_policy": self.image_pull_policy.value,
            "command": self.get_command(),
            "args": self.get_args(),
            "source": self.get_script(),
            # "resources": self.argo_resources,
            "env": self.env,
            "env_from": self.env_from,
            "working_dir": self.working_dir,
            "volume_mounts": self.get_volume_mounts(),
            "security_context": self.get_security_context(),
        }
        script_kargs = {k: v for k, v in script_kwargs.items() if v is not None}
        template = IoArgoprojWorkflowV1alpha1ScriptTemplate(**script_kargs)
        return template

    def get_security_context(self) -> Optional[SecurityContext]:
        """Assembles the security context for the task.

        Returns
        -------
        Optional[SecurityContext]
            The security settings to apply to the task's container.
        """
        if not self.security_context:
            return None
        return self.security_context.get_security_context()

    def get_container(self) -> Container:
        """Assembles and returns the container for the task to run in.

        Returns
        -------
        Container
            The container template representation of the task.
        """
        container_kwargs = {
            "image": self.image,
            "image_pull_policy": self.image_pull_policy.value,
            "command": self.get_command(),
            "volume_mounts": self.get_volume_mounts(),
            "resources": self.argo_resources,
            "args": self.get_args(),
            "env": self.env,
            "env_from": self.env_from,
            "working_dir": self.working_dir,
            "security_context": self.get_security_context(),
        }
        container_args = {k: v for k, v in container_kwargs.items() if v is not None}
        container = Container(**container_args)
        return container

    def assemble_task_template(self) -> IoArgoprojWorkflowV1alpha1Template:
        """Assembles and returns the template that contains the specification of the parameters, inputs, and other
        configuration required for the task be executed.

        Returns
        -------
        IoArgoprojWorkflowV1alpha1Template
            The template representation of the task.
        """
        template = IoArgoprojWorkflowV1alpha1Template(
            name=self.name,
            daemon=self.daemon,
            inputs=self.argo_inputs,
            outputs=self.argo_outputs,
            tolerations=self.get_tolerations(),
            metadata=IoArgoprojWorkflowV1alpha1Metadata(labels=self.labels, annotations=self.annotations),
        )
        if self.node_selector:
            setattr(template, "node_selector", self.node_selector)

        retry_strategy = self.get_retry_strategy()
        if retry_strategy:
            setattr(template, "retry_strategy", retry_strategy)

        script_def = self.get_script_def()
        if script_def:
            setattr(template, "script", self.get_script_def())
        else:
            setattr(template, "container", self.get_container())

        affinity = self.affinity.get_spec() if self.affinity else None
        if affinity is not None:
            setattr(template, "affinity", affinity)

        if self.memoize:
            setattr(template, "memoize", self.memoize.get_spec())

        return template

    def get_retry_strategy(self) -> Optional[IoArgoprojWorkflowV1alpha1RetryStrategy]:
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

    def get_tolerations(self) -> List[ArgoToleration]:
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

        ts = []
        for t in self.tolerations:
            ts.append(ArgoToleration(key=t.key, effect=t.effect, operator=t.operator, value=t.value))
        return ts if ts else []

    def get_continue_on(self) -> Optional[IoArgoprojWorkflowV1alpha1ContinueOn]:
        """Assembles and returns the `continue_on` task setting"""
        if self.continue_on_error and self.continue_on_fail:
            return IoArgoprojWorkflowV1alpha1ContinueOn(error=True, failed=True)
        elif self.continue_on_error:
            return IoArgoprojWorkflowV1alpha1ContinueOn(error=True)
        elif self.continue_on_fail:
            return IoArgoprojWorkflowV1alpha1ContinueOn(failed=True)
        return None

    def get_spec(self) -> IoArgoprojWorkflowV1alpha1DAGTask:
        """Assembles and returns the graph task specification of the task.

        Returns
        -------
        V1alpha1DAGTask
            The graph task representation.
        """
        task = IoArgoprojWorkflowV1alpha1DAGTask(
            name=self.name,
            arguments=self.argo_arguments,
            _check_type=False,
        )
        if self.continue_on_error or self.continue_on_fail:
            setattr(task, "continue_on", self.get_continue_on())

        if self.template_ref:
            setattr(task, "template_ref", self.template_ref.argo_spec)
        else:
            setattr(task, "template", self.argo_template.name)

        if self.with_param:
            setattr(task, "with_param", self.with_param)
        return task


def _dependencies_to_depends(dependencies: List[str]) -> str:
    if not dependencies or len(dependencies) == 0:
        return ""
    depends = f"{dependencies[0]}"
    for dep in dependencies[1:]:
        depends += f" && {dep}"
    return depends
