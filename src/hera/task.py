"""The implementation of a Hera task for Argo workflows"""

import copy
import inspect
import json
import textwrap
from typing import Any, Callable, Dict, List, Optional, Set, Union

from argo_workflows.model.security_context import SecurityContext
from argo_workflows.model_utils import (
    ApiTypeError,
    ModelSimple,
    cached_property,
    convert_js_args_to_python_args,
)
from argo_workflows.models import (
    Container,
    EnvVar,
    IoArgoprojWorkflowV1alpha1Arguments,
    IoArgoprojWorkflowV1alpha1Artifact,
    IoArgoprojWorkflowV1alpha1Backoff,
    IoArgoprojWorkflowV1alpha1DAGTask,
    IoArgoprojWorkflowV1alpha1Inputs,
    IoArgoprojWorkflowV1alpha1Metadata,
    IoArgoprojWorkflowV1alpha1Outputs,
    IoArgoprojWorkflowV1alpha1Parameter,
    IoArgoprojWorkflowV1alpha1RetryStrategy,
    IoArgoprojWorkflowV1alpha1ScriptTemplate,
    IoArgoprojWorkflowV1alpha1Template,
    ResourceRequirements,
)
from argo_workflows.models import Toleration as ArgoToleration
from argo_workflows.models import VolumeMount
from pydantic import BaseModel

from hera.artifact import Artifact, OutputArtifact
from hera.env import EnvSpec
from hera.input import InputFrom
from hera.operator import Operator
from hera.resources import Resources
from hera.retry import Retry
from hera.security_context import TaskSecurityContext
from hera.toleration import Toleration


class _Item(ModelSimple):
    """
    When we use a DAG task's `with_items` field, we typically pass in a list of dictionaries as (str, str). The problem
    with the auto-generated `argo_workflows` SDK, however, is that it will attempt to interpret each element in this
    list of `with_items` as a non-primitive type, ultimately attempting to convert it to an internal representation,
    which, clearly, does not exist. This happens during the call to `argo_workflows.model_utils.model_to_dict()`, which
    recursively calls `model_to_dict` on the elements present in `with_items`. Since each element is a primitive `dict`
    that does not have the methods necessary for `model_to_dict`, we get SDK exceptions during workflow/task
    submission. To overcome this by not modifying the SDK, we can implement our own wrapper around a primitive type
    by using `ModelSimple`. The `ParallelSteps` construct, of the SDK, is a wrapper around a primitive `list`/`array`,
    and it uses a similar structure. This implementation is very similar to `ParallelSteps` but uses `dict` rather
    than internal `str` and `list`.
    """

    allowed_values: Dict[Any, Any] = {}

    validations: Dict[Any, Any] = {}

    @cached_property
    def openapi_types():  # type: ignore
        """
        This must be a method because a model may have properties that are of type self, this must run
        after the class is loaded.
        """
        return {
            'value': (dict,),
        }

    @cached_property
    def discriminator():  # type: ignore
        """
        Typically returns an internal SDK class that can be used to discriminate between inheriting
        classes, not necessary in this case.
        """
        return None

    attribute_map: Dict[Any, Any] = {}
    read_only_vars: Set[Any] = set()
    _composed_schemas = None
    required_properties = set(
        [
            '_data_store',
            '_check_type',
            '_spec_property_naming',
            '_path_to_item',
            '_configuration',
            '_visited_composed_classes',
        ]
    )

    @convert_js_args_to_python_args
    def __init__(self, *args, **kwargs):
        # required up here when default value is not given
        _path_to_item = kwargs.pop('_path_to_item', ())

        if 'value' in kwargs:
            value = kwargs.pop('value')
        elif args:
            args = list(args)  # type: ignore
            value = args.pop(0)  # type: ignore
        else:
            raise ApiTypeError(
                "value is required, but not passed in args or kwargs and doesn't have default",
                path_to_item=_path_to_item,
                valid_classes=(self.__class__,),
            )

        _check_type = kwargs.pop('_check_type', True)
        _spec_property_naming = kwargs.pop('_spec_property_naming', False)
        _configuration = kwargs.pop('_configuration', None)
        _visited_composed_classes = kwargs.pop('_visited_composed_classes', ())

        if args:
            raise ApiTypeError(
                "Invalid positional arguments=%s passed to %s. Remove those invalid positional arguments."
                % (
                    args,
                    self.__class__.__name__,
                ),
                path_to_item=_path_to_item,
                valid_classes=(self.__class__,),
            )

        self._data_store = {}
        self._check_type = _check_type
        self._spec_property_naming = _spec_property_naming
        self._path_to_item = _path_to_item
        self._configuration = _configuration
        self._visited_composed_classes = _visited_composed_classes + (self.__class__,)
        self.value = value
        if kwargs:
            raise ApiTypeError(
                "Invalid named arguments=%s passed to %s. Remove those invalid named arguments."
                % (
                    kwargs,
                    self.__class__.__name__,
                ),
                path_to_item=_path_to_item,
                valid_classes=(self.__class__,),
            )


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
    image: str = 'python:3.7'
        The image to use in the execution of the function.
    daemon: Optional[bool] = None
        Wether to run the the task as daemon.
    command: Optional[List[str]] = None
        The command to use in the environment where the function runs in order to run the specific function. Note that
        the specified function is parsed, stored as a string, and ultimately placed in a separate file inside the task
        and invoked via `python script_file.py`. This command offers users the opportunity to start up the script in a
        different way e.g `time python` to time execution, `horovodrun -p X` to use horovod from an image that allows
        training models on multiple GPUs, etc.
    env_specs: Optional[List[EnvSpec]] = None
        The environment specifications to load. This operates on a single Enum that specifies whether to load the AWS
        credentials, or other available secrets.
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
    security_context: Optional[TaskSecurityContext] = None
        Define security settings for the task container, overrides workflow security context.
    """

    def __init__(
        self,
        name: str,
        func: Optional[Callable] = None,
        func_params: Optional[List[Dict[str, Union[int, str, float, dict, BaseModel]]]] = None,
        input_from: Optional[InputFrom] = None,
        input_artifacts: Optional[List[Artifact]] = None,
        output_artifacts: Optional[List[OutputArtifact]] = None,
        image: str = 'python:3.7',
        daemon: bool = False,
        command: Optional[List[str]] = None,
        env_specs: Optional[List[EnvSpec]] = None,
        resources: Resources = Resources(),
        working_dir: Optional[str] = None,
        retry: Optional[Retry] = None,
        tolerations: Optional[List[Toleration]] = None,
        node_selectors: Optional[Dict[str, str]] = None,
        labels: Optional[Dict[str, str]] = None,
        security_context: Optional[TaskSecurityContext] = None,
    ):
        self.name = name.replace("_", "-")  # RFC1123
        self.func = func
        self.func_params = func_params
        self.input_from = input_from
        self.input_artifacts = input_artifacts
        self.output_artifacts = output_artifacts
        self.validate()

        self.image = image
        self.daemon = daemon
        self.command = command if command else ['python']
        self.env = self.get_env(env_specs)
        self.resources = resources
        self.working_dir = working_dir
        self.retry = retry
        self.tolerations = tolerations
        self.node_selector = node_selectors
        self.labels = labels or {}
        self.security_context = security_context

        self.parameters = self.get_parameters()
        self.argo_input_artifacts = self.get_argo_input_artifacts()
        self.argo_output_artifacts = self.get_argo_output_artifacts()
        self.arguments = self.get_arguments()
        self.inputs = self.get_inputs()
        self.outputs = self.get_outputs()
        self.argo_resources = self.get_resources()
        self.argo_template = self.get_task_template()
        self.argo_task = self.get_task_spec()

    def next(self, other: 'Task') -> 'Task':
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
        if not hasattr(other.argo_task, 'dependencies'):
            setattr(other.argo_task, 'dependencies', [self.argo_task.name])
        else:
            other.argo_task.dependencies.append(self.argo_task.name)
        return other

    def __rshift__(self, other: 'Task') -> 'Task':
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

    def when(self, other: 'Task', operator: Operator, value: str) -> 'Task':
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
        self.argo_task.when = f'{{{{tasks.{other.name}.outputs.result}}}} {operator.value} {value}'
        return other.next(self)

    def validate(self):
        """
        Validates that the given function and corresponding params fit one another, raises AssertionError if
        conditions are not satisfied.
        """
        # verify artifacts are uniquely names
        if self.input_artifacts:
            assert len(set([i.name for i in self.input_artifacts])) == len(
                self.input_artifacts
            ), 'input artifact names must be unique'
        if self.output_artifacts:
            assert len(set([i.name for i in self.output_artifacts])) == len(
                self.output_artifacts
            ), 'output artifact names must be unique'

        if self.func:
            self._validate_func()

    def _validate_func(self):
        args = set(inspect.getfullargspec(self.func).args)
        if args:
            if self.input_from:
                assert self.input_artifacts is None, 'cannot supply both InputFrom and Artifacts'

                # input_from denotes the task will receive input from another step. This leaves it up to the
                # client to set up the proper output in a previous task
                if self.func_params:
                    # only single func params are allowed if they are specified along with input_from
                    assert (
                        len(self.func_params) == 1
                    ), 'only single function parameters are allowed when specified together with input_from'
                pass
            else:
                signature = inspect.signature(self.func)
                keywords = []

                if list(signature.parameters.values()):
                    for param in list(signature.parameters.values()):
                        if (
                            param.default != inspect.Parameter.empty
                            and param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
                        ):
                            keywords.append(param.name)
                if len(keywords) == len(args):
                    pass  # these are all kwargs, safe to skip
                else:
                    # otherwise, it must be the case that the client passes func_params
                    assert self.func_params, 'no parameters passed for function'
        if self.func_params:
            for params in self.func_params:
                assert args.issuperset(set(params.keys())), 'mismatched function arguments and passed parameters'

    def get_argo_input_artifacts(self) -> List[IoArgoprojWorkflowV1alpha1Artifact]:
        """Assembles and returns a list of artifacts assembled from the Hera internal input artifact representation"""
        if not self.input_artifacts:
            return []
        input_artifacts = [i.get_spec() for i in self.input_artifacts]
        return input_artifacts if input_artifacts else []

    def get_argo_output_artifacts(self) -> List[IoArgoprojWorkflowV1alpha1Artifact]:
        """Assembles and returns a list of artifacts assembled from the Hera internal output artifact representation"""
        if not self.output_artifacts:
            return []
        output_artifacts = [o.get_spec() for o in self.output_artifacts]
        return output_artifacts if output_artifacts else []

    def get_arguments(self) -> IoArgoprojWorkflowV1alpha1Arguments:
        """Assembles and returns the task arguments"""
        return IoArgoprojWorkflowV1alpha1Arguments(parameters=self.parameters, artifacts=self.argo_input_artifacts)

    def get_inputs(self) -> IoArgoprojWorkflowV1alpha1Inputs:
        """Assembles the inputs of the task.
        Returns
        -------
        IoArgoprojWorkflowV1alpha1Inputs

        Notes
        -----
        Note that this parses specified artifacts differently than `get_argo_input_artifacts`.
        """
        artifacts = []
        if self.argo_input_artifacts:
            artifacts = [i.get_input_spec() for i in self.input_artifacts]
        return IoArgoprojWorkflowV1alpha1Inputs(parameters=self.parameters, artifacts=artifacts)

    def get_outputs(self) -> IoArgoprojWorkflowV1alpha1Outputs:
        """Assembles and returns the task outputs"""
        return IoArgoprojWorkflowV1alpha1Outputs(artifacts=self.argo_output_artifacts)

    def get_command(self) -> List[str]:
        """
        Parses and returns the specified task command. This will attempt to stringify every command option and
        raise a ValueError on failure.
        """
        assert self.command
        return [str(cc) for cc in self.command]

    def get_env(self, specs: List[EnvSpec]) -> Optional[List[EnvVar]]:
        """Returns a list of Argo workflow environment variables based on the specified Hera environment specifications.

        Parameters
        ----------
        specs: List[EnvSpec]
            Hera environment specifications.

        Returns
        -------
        Optional[List[EnvVar]]
            A list of Argo environment specifications, if any specs are provided.
        """
        if not specs:
            return None
        r = []
        for spec in specs:
            r.append(spec.argo_spec)
        return r

    def get_parameters(self) -> List[IoArgoprojWorkflowV1alpha1Parameter]:
        """Returns a list of Argo workflow task parameters based on the specified task function parameters.

        Returns
        -------
        List[IoArgoprojWorkflowV1alpha1Parameter]
            The list of constructed Argo parameters.

        Notes
        -----
        If users specify keyword parameters in the func_params payload those will override the kwarg specified in the
        task function parameters.
        """
        parameters = []

        if self.input_from:
            # this represents input from another step, which only requires parameter name specifications
            # the intersection between arg specifications and input_from parameters represents the arguments
            # that come in from other tasks
            args = set(inspect.getfullargspec(self.func).args).intersection(set(self.input_from.parameters))
            for arg in args:
                parameters.append(IoArgoprojWorkflowV1alpha1Parameter(name=arg, value=f'{{{{item.{arg}}}}}'))
        if self.func:
            parameters += self.get_func_parameters()

        return parameters

    def get_func_parameters(self) -> List[IoArgoprojWorkflowV1alpha1Parameter]:
        """Returns a list of Argo workflow parameters that are for the function passed to the task

        Returns
        -------
        List[IoArgoprojWorkflowV1alpha1Parameter]
            The list of constructed Argo parameters.
        """
        parameters = []
        param_name_cache = set()
        # if there are any keyword arguments associated with the function signature, we set them as default values
        # so Argo passes them in
        signature = inspect.signature(self.func)
        keywords = []

        if list(signature.parameters.values()):
            for param in list(signature.parameters.values()):
                if param.default != inspect.Parameter.empty and param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                    keywords.append([param.name, param.default])

        if self.func_params:
            if len(self.func_params) == 1:
                # if there's a single func_param dict, then we need to map each input key and value pair to a valid
                # JSON parameter entry
                for param_name, param_value in self.func_params[0].items():
                    if isinstance(param_value, BaseModel):
                        value = param_value.json()
                    else:
                        value = json.dumps(param_value)
                    parameters.append(IoArgoprojWorkflowV1alpha1Parameter(name=param_name, value=value))
                    param_name_cache.add(param_name)
            elif len(self.func_params) > 1:
                # at this point the init passed validation, so this condition is always false when self.input_from
                # is specified

                # if there's more than 1 input, it's a parallel task so we map the param names of the
                # first series of params to item.param_name since the keys are all the same for the func_params
                for param_name in self.func_params[0].keys():
                    parameters.append(
                        IoArgoprojWorkflowV1alpha1Parameter(name=param_name, value=f'{{{{item.{param_name}}}}}')
                    )
                    param_name_cache.add(param_name)
        for name, value in keywords:
            if isinstance(value, BaseModel):
                value = value.json()
            else:
                value = json.dumps(value)
            if name in param_name_cache:
                continue  # user override of a kwarg
            parameters.append(IoArgoprojWorkflowV1alpha1Parameter(name=name, value=value))
        return parameters

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
        for param in self.arguments.parameters:
            extract += f"""{param.name} = json.loads('{{{{inputs.parameters.{param.name}}}}}')\n"""
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
        script_extra = self.get_param_script_portion()

        script = ''
        if script_extra:
            script = copy.deepcopy(script_extra)
            script += '\n'

        # content represents the function components, separated by new lines
        # therefore, the actual code block occurs after the end parenthesis, which is a literal `):\n`
        content = inspect.getsourcelines(self.func)[0]
        token_index, start_token = 1, ':\n'
        for curr_index, curr_token in enumerate(content):
            if start_token in curr_token:
                # when we find the curr token we find the end of the function header. The next index is the
                # starting point of the function body
                token_index = curr_index + 1
                break

        s = "".join(content[token_index:])
        script += textwrap.dedent(s)
        return textwrap.dedent(script)

    def get_resources(self) -> ResourceRequirements:
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
                'cpu': str(self.resources.min_cpu),
                'memory': self.resources.min_mem,
            },
            limits={
                'cpu': str(self.resources.max_cpu) if max_cpu else str(self.resources.min_cpu),
                'memory': self.resources.max_mem if max_mem else self.resources.min_mem,
            },
        )

        if self.resources.min_custom_resources is not None:
            resource.requests.update(**self.resources.min_custom_resources)

        if max_custom:
            resource.limits.update(**self.resources.max_custom_resources)
        elif self.resources.min_custom_resources:
            resource.limits.update(**self.resources.min_custom_resources)

        if self.resources.gpus:
            resource.requests['nvidia.com/gpu'] = str(self.resources.gpus)
            resource.limits['nvidia.com/gpu'] = str(self.resources.gpus)
        return resource

    def get_parallel_items(self) -> List[_Item]:
        """Constructs a list of items to be used in a parallel task. This is typically consumed in order to be passed
        to the with_items field of an Argo DAG task.

        Returns
        -------
        List[_Item]
            A list of dictionaries keyed by the argument name to the argument value.
        """
        items: List[_Item] = []
        if not self.func_params:
            return items

        for func_param in self.func_params:
            item = {}
            for k, v in func_param.items():
                if isinstance(v, BaseModel):
                    item[k] = v.json()
                else:
                    item[k] = json.dumps(v)  # type: ignore
            items.append(_Item(value=item))
        return items

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

        template = IoArgoprojWorkflowV1alpha1ScriptTemplate(
            name=self.name,
            image=self.image,
            command=self.get_command(),
            source=self.get_script(),
            resources=self.argo_resources,
        )
        if self.security_context:
            security_context = self.security_context.get_security_context()
            setattr(template, 'security_context', security_context)
        if self.working_dir:
            setattr(template, 'working_dir', self.working_dir)
        if self.env:
            setattr(template, 'env', self.env)
        return template

    def get_security_context(self) -> SecurityContext:
        """Assembles the security context for the task.

        Returns
        -------
        SecurityContext
            The security settings to apply to the task's container.
        """
        return self.security_context.get_security_context()

    def get_container(self) -> Container:
        """Assembles and returns the container for the task to run in.

        Returns
        -------
        Container
            The container template representation of the task.
        """
        container = Container(
            image=self.image,
            command=self.get_command(),
            volume_mounts=self.get_volume_mounts(),
            resources=self.argo_resources,
        )
        if self.security_context:
            security_context = self.get_security_context()
            setattr(container, 'env', security_context)
        if self.env:
            setattr(container, 'env', self.env)
        if self.working_dir:
            setattr(container, 'working_dir', self.working_dir)
        return container

    def get_task_template(self) -> IoArgoprojWorkflowV1alpha1Template:
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
            inputs=self.inputs,
            outputs=self.outputs,
            tolerations=self.get_tolerations(),
            metadata=IoArgoprojWorkflowV1alpha1Metadata(labels=self.labels),
        )
        if self.node_selector:
            setattr(template, 'node_selector', self.node_selector)

        retry_strategy = self.get_retry_strategy()
        if retry_strategy:
            setattr(template, 'retry_strategy', retry_strategy)

        if self.get_script_def():
            setattr(template, 'script', self.get_script_def())
        else:
            setattr(template, 'container', self.get_container())
        return template

    def get_retry_strategy(self) -> Optional[IoArgoprojWorkflowV1alpha1RetryStrategy]:
        """Assembles and returns a retry strategy for the task. This is dictated by the task `retry_limit`.

        Returns
        -------
        Optional[IoArgoprojWorkflowV1alpha1RetryStrategy]
            A V1alpha1RetryStrategy object if `retry_limit` is specified, None otherwise.
        """
        if self.retry:
            return IoArgoprojWorkflowV1alpha1RetryStrategy(
                backoff=IoArgoprojWorkflowV1alpha1Backoff(
                    duration=str(self.retry.duration), max_duration=str(self.retry.max_duration)
                )
            )
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

    def get_task_spec(self) -> IoArgoprojWorkflowV1alpha1DAGTask:
        """Assembles and returns the graph task specification of the task.

        Returns
        -------
        V1alpha1DAGTask
            The graph task representation.
        """
        if self.input_from:
            return IoArgoprojWorkflowV1alpha1DAGTask(
                name=self.name,
                template=self.argo_template.name,
                arguments=self.arguments,
                with_param=f'{{{{tasks.{self.input_from.name}.outputs.result}}}}',
            )
        if self.func_params and len(self.func_params) > 1:
            items = self.get_parallel_items()
            return IoArgoprojWorkflowV1alpha1DAGTask(
                name=self.name,
                template=self.argo_template.name,
                dependencies=[],
                arguments=self.arguments,
                with_items=items,
                _check_type=False,
            )
        return IoArgoprojWorkflowV1alpha1DAGTask(
            name=self.name, template=self.argo_template.name, arguments=self.arguments
        )
