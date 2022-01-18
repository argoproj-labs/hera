"""The implementation of a Hera task for Argo workflows"""

import copy
import inspect
import json
import textwrap
from typing import Any, Callable, Dict, List, Optional, Union

from argo.workflows.client import (
    V1alpha1Arguments,
    V1alpha1Artifact,
    V1alpha1Backoff,
    V1alpha1DAGTask,
    V1alpha1Inputs,
    V1alpha1Outputs,
    V1alpha1Parameter,
    V1alpha1RetryStrategy,
    V1alpha1ScriptTemplate,
    V1alpha1Template,
    V1EnvVar,
    V1ResourceRequirements,
    V1Toleration,
    V1VolumeMount,
)
from pydantic import BaseModel

from hera.artifact import InputArtifact, OutputArtifact
from hera.env import EnvSpec
from hera.input import InputFrom
from hera.operator import Operator
from hera.resources import Resources
from hera.retry import Retry
from hera.toleration import Toleration


class Task:
    """An Argo task representation. This is used to submit functions to be executed on Argo.

    The task can take a function, along with its parameters, resource configuration, a volume, etc, and submit it for
    remote execution.

    Parameters
    ----------
    name: str
        The name of the task to submit as part of a workflow.
    func: Callable
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
    """

    def __init__(
        self,
        name: str,
        func: Callable,
        func_params: Optional[List[Dict[str, Union[int, str, float, dict, BaseModel]]]] = None,
        input_from: Optional[InputFrom] = None,
        input_artifacts: Optional[List[InputArtifact]] = None,
        output_artifacts: Optional[List[OutputArtifact]] = None,
        image: str = 'python:3.7',
        daemon: Optional[bool] = None,
        command: Optional[List[str]] = None,
        env_specs: Optional[List[EnvSpec]] = None,
        resources: Resources = Resources(),
        working_dir: Optional[str] = None,
        retry: Optional[Retry] = None,
        tolerations: Optional[List[Toleration]] = None,
        node_selectors: Optional[Dict[str, str]] = None,
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
        self.node_selectors = node_selectors

        self.parameters = self.get_parameters()
        self.argo_input_artifacts = self.get_argo_input_artifacts()
        self.argo_output_artifacts = self.get_argo_output_artifacts()
        self.arguments = self.get_arguments()
        self.inputs = self.get_inputs()
        self.outputs = self.get_outputs()
        self.argo_resources = self.get_resources()
        self.script_extra = self.get_param_script_portion()
        self.script = self.get_script()
        self.script_def = self.get_script_def()
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
        assert isinstance(other, self.__class__)
        if not other.argo_task.dependencies:
            other.argo_task.dependencies = [self.argo_task.name]
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

    def get_argo_input_artifacts(self) -> Optional[List[V1alpha1Artifact]]:
        """Assembles and returns a list of artifacts assembled from the Hera internal input artifact representation"""
        if not self.input_artifacts:
            return None
        input_artifacts = [i.get_spec() for i in self.input_artifacts]
        return input_artifacts if input_artifacts else None

    def get_argo_output_artifacts(self) -> Optional[List[V1alpha1Artifact]]:
        """Assembles and returns a list of artifacts assembled from the Hera internal output artifact representation"""
        if not self.output_artifacts:
            return None
        output_artifacts = [o.get_spec() for o in self.output_artifacts]
        return output_artifacts if output_artifacts else None

    def get_arguments(self) -> V1alpha1Arguments:
        """Assembles and returns the task arguments"""
        return V1alpha1Arguments(parameters=self.parameters, artifacts=self.argo_input_artifacts)

    def get_inputs(self) -> V1alpha1Inputs:
        """Assembles the inputs of the task.
        Returns
        -------
        V1alpha1Inputs

        Notes
        -----
        Note that this parses specified artifacts differently than `get_argo_input_artifacts`.
        """
        input_art = None
        if self.argo_input_artifacts:
            input_art = [V1alpha1Artifact(name=a.name, path=a.path) for a in self.argo_input_artifacts]
        return V1alpha1Inputs(parameters=self.parameters, artifacts=input_art)

    def get_outputs(self) -> V1alpha1Outputs:
        """Assembles and returns the task outputs"""
        return V1alpha1Outputs(artifacts=self.argo_output_artifacts)

    def get_command(self) -> List[str]:
        """
        Parses and returns the specified task command. This will attempt to stringify every command option and
        raise a ValueError on failure.
        """
        assert self.command
        return [str(cc) for cc in self.command]

    def get_env(self, specs: List[EnvSpec]) -> Optional[List[V1EnvVar]]:
        """Returns a list of Argo workflow environment variables based on the specified Hera environment specifications.

        Parameters
        ----------
        specs: List[EnvSpec]
            Hera environment specifications.

        Returns
        -------
        Optional[List[V1EnvVar]]
            A list of Argo environment specifications, if any specs are provided.
        """
        if not specs:
            return None
        r = []
        for spec in specs:
            r.append(spec.argo_spec)
        return r

    def get_parameters(self) -> List[V1alpha1Parameter]:
        """Returns a list of Argo workflow task parameters based on the specified task function parameters.

        Returns
        -------
        List[V1alpha1Parameter]
            The list of constructed Argo parameters.

        Notes
        -----
        If users specify keyword parameters in the func_params payload those will override the kwarg specified in the
        task function parameters.
        """
        parameters = []
        param_name_cache = set()

        if self.input_from:
            # this represents input from another step, which only requires parameter name specifications
            # the intersection between arg specifications and input_from parameters represents the arguments
            # that come in from other tasks
            args = set(inspect.getfullargspec(self.func).args).intersection(set(self.input_from.parameters))
            for arg in args:
                parameters.append(V1alpha1Parameter(name=arg, value=f'{{{{item.{arg}}}}}'))

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
                    parameters.append(V1alpha1Parameter(name=param_name, value=value))
                    param_name_cache.add(param_name)
            elif len(self.func_params) > 1:
                # at this point the init passed validation, so this condition is always false when self.input_from
                # is specified

                # if there's more than 1 input, it's a parallel task so we map the param names of the
                # first series of params to item.param_name since the keys are all the same for the func_params
                for param_name in self.func_params[0].keys():
                    parameters.append(V1alpha1Parameter(name=param_name, value=f'{{{{item.{param_name}}}}}'))
                    param_name_cache.add(param_name)

        for name, value in keywords:
            if isinstance(value, BaseModel):
                value = value.json()
            else:
                value = json.dumps(value)
            if name in param_name_cache:
                continue  # user override of a kwarg
            parameters.append(V1alpha1Parameter(name=name, value=value))
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

        Examples
        --------
        > args = V1alpha1Arguments(parameters=V1alpha1Parameter(name='a', value='whatever'))
        > script = get_param_script_portion(args)
        > print(script)
        import json
        a = json.loads('{{inputs.parameters.a}}')
        print(a)  # prints 'whatever'
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
        script = ''
        if self.script_extra:
            script = copy.deepcopy(self.script_extra)
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

    def get_resources(self) -> V1ResourceRequirements:
        """Assembles an Argo resource requirements object with the given resource configuration.

        Returns
        -------
        V1ResourceRequirements
            A configured Argo resource requirement with the given configuration.
        """
        max_cpu = self.resources.max_cpu is not None
        max_mem = self.resources.max_mem is not None
        resource = V1ResourceRequirements(
            requests={
                'cpu': str(self.resources.min_cpu),
                'memory': self.resources.min_mem,
            },
            limits={
                'cpu': str(self.resources.max_cpu) if max_cpu else str(self.resources.min_cpu),
                'memory': self.resources.max_mem if max_mem else self.resources.min_mem,
            },
        )

        if self.resources.gpus:
            resource.requests['nvidia.com/gpu'] = str(self.resources.gpus)
            resource.limits['nvidia.com/gpu'] = str(self.resources.gpus)
        return resource

    def get_parallel_items(self) -> List[Dict[str, str]]:
        """Constructs a list of items to be used in a parallel task. This is typically consumed in order to be passed
        to the with_items field of an Argo DAG task.

        Returns
        -------
        List[Dict[str, str]]
            A list of dictionaries keyed by the argument name to the argument value.
        """
        items: List[Dict[str, Any]] = []
        if not self.func_params:
            return items

        for func_param in self.func_params:
            item = {}
            for k, v in func_param.items():
                if isinstance(v, BaseModel):
                    item[k] = v.json()
                else:
                    item[k] = json.dumps(v)
            items.append(item)
        return items

    def get_volume_mounts(self) -> List[V1VolumeMount]:
        """Assembles the list of volumes to be mounted by the task.

        Returns
        -------
        List[V1VolumeMount]
            The list of volume mounts to be added to the task specification.
        """
        volumes = []
        if self.resources.volume:
            volumes.append(self.resources.volume.get_mount())
        if self.resources.existing_volume:
            volumes.append(self.resources.existing_volume.get_mount())
        if self.resources.empty_dir_volume:
            volumes.append(self.resources.empty_dir_volume.get_mount())
        return volumes

    def get_script_def(self) -> V1alpha1ScriptTemplate:
        """Assembles and returns the script template that contains the definition of the script to run in a task.

        Returns
        -------
        V1alpha1ScriptTemplate
            The script template representation of the task.
        """
        return V1alpha1ScriptTemplate(
            name=self.name,
            command=self.get_command(),
            source=self.script,
            image=self.image,
            env=self.env,
            resources=self.argo_resources,
            volume_mounts=self.get_volume_mounts(),
            working_dir=self.working_dir,
        )

    def get_task_template(self) -> V1alpha1Template:
        """Assembles and returns the template that contains the specification of the parameters, inputs, and other
        configuration required for the task be executed.

        Returns
        -------
        V1alpha1Template
            The template representation of the task.
        """
        return V1alpha1Template(
            name=self.name,
            daemon=self.daemon,
            script=self.script_def,
            arguments=self.arguments,
            inputs=self.inputs,
            outputs=self.outputs,
            node_selector=self.node_selectors,
            tolerations=self.get_tolerations(),
            retry_strategy=self.get_retry_strategy(),
        )

    def get_retry_strategy(self) -> Optional[V1alpha1RetryStrategy]:
        """Assembles and returns a retry strategy for the task. This is dictated by the task `retry_limit`.

        Returns
        -------
        Optional[V1alpha1RetryStrategy]
            A V1alpha1RetryStrategy object if `retry_limit` is specified, None otherwise.
        """
        if self.retry is not None:
            return V1alpha1RetryStrategy(
                backoff=V1alpha1Backoff(duration=str(self.retry.duration), max_duration=str(self.retry.max_duration))
            )
        return None

    def get_tolerations(self) -> Optional[List[V1Toleration]]:
        """Assembles and returns the pod toleration objects required for scheduling a task.

        Returns
        -------
        Optional[List[V1Toleration]]
            The list of assembled tolerations.

        Notes
        -----
        If the task includes a GPU resource specification the client is responsible for specifying a GPU toleration.
        For GKE and Azure workloads `hera.v1.tolerations.GPUToleration` can be specified.
        """
        if self.tolerations is None:
            return None

        ts = []
        for t in self.tolerations:
            ts.append(V1Toleration(key=t.key, effect=t.effect, operator=t.operator, value=t.value))

        return ts if ts else None

    def get_task_spec(self) -> V1alpha1DAGTask:
        """Assembles and returns the graph task specification of the task.

        Returns
        -------
        V1alpha1DAGTask
            The graph task representation.
        """
        if self.input_from:
            return V1alpha1DAGTask(
                name=self.name,
                template=self.argo_template.name,
                arguments=self.arguments,
                with_param=f'{{{{tasks.{self.input_from.name}.outputs.result}}}}',
            )
        if self.func_params and len(self.func_params) > 1:
            items = self.get_parallel_items()
            return V1alpha1DAGTask(
                name=self.name, template=self.argo_template.name, arguments=self.arguments, with_items=items
            )
        return V1alpha1DAGTask(name=self.name, template=self.argo_template.name, arguments=self.arguments)
