from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set, TypeVar, Union, cast

from pydantic import root_validator, validator

from hera.shared import BaseMixin, global_config
from hera.shared.serialization import serialize
from hera.workflows._context import SubNodeMixin, _context
from hera.workflows.artifact import Artifact
from hera.workflows.env import Env, _BaseEnv
from hera.workflows.env_from import _BaseEnvFrom
from hera.workflows.exceptions import InvalidTemplateCall, InvalidType
from hera.workflows.metrics import Metrics, _BaseMetric
from hera.workflows.models import (
    HTTP,
    Affinity,
    Arguments as ModelArguments,
    Artifact as ModelArtifact,
    ArtifactLocation,
    ContainerPort,
    ContinueOn,
    EnvFromSource,
    EnvVar,
    ExecutorConfig,
    HostAlias,
    ImagePullPolicy,
    Inputs as ModelInputs,
    IntOrString,
    Item,
    LifecycleHook,
    Memoize,
    Metadata,
    Metrics as ModelMetrics,
    Outputs as ModelOutputs,
    Parameter as ModelParameter,
    PersistentVolumeClaim,
    Plugin,
    PodSecurityContext,
    Probe,
    Prometheus as ModelPrometheus,
    ResourceRequirements,
    RetryStrategy,
    Sequence,
    Synchronization,
    Template,
    TemplateRef,
    TerminationMessagePolicy,
    Toleration,
    UserContainer as ModelUserContainer,
    Volume as ModelVolume,
    VolumeDevice,
    VolumeMount,
)
from hera.workflows.parameter import MISSING, Parameter
from hera.workflows.protocol import Templatable
from hera.workflows.resources import Resources
from hera.workflows.user_container import UserContainer
from hera.workflows.volume import Volume, _BaseVolume

if TYPE_CHECKING:
    from hera.workflows.steps import Step
    from hera.workflows.task import Task


InputsT = Optional[
    Union[
        ModelInputs,
        Union[Parameter, ModelParameter, Artifact, ModelArtifact, Dict[str, Any]],
        List[Union[Parameter, ModelParameter, Artifact, ModelArtifact, Dict[str, Any]]],
    ]
]
OutputsT = Optional[
    Union[
        ModelOutputs,
        Union[Parameter, ModelParameter, Artifact, ModelArtifact],
        List[Union[Parameter, ModelParameter, Artifact, ModelArtifact]],
    ]
]
ArgumentsT = Optional[
    Union[
        ModelArguments,
        Union[Parameter, ModelParameter, Artifact, ModelArtifact, Dict[str, Any]],
        List[Union[Parameter, ModelParameter, Artifact, ModelArtifact, Dict[str, Any]]],
    ]
]
EnvT = Optional[
    Union[
        _BaseEnv,
        EnvVar,
        List[Union[_BaseEnv, EnvVar, Dict[str, Any]]],
        Dict[str, Any],
    ]
]
EnvFromT = Optional[Union[_BaseEnvFrom, EnvFromSource, List[Union[_BaseEnvFrom, EnvFromSource]]]]
VolumesT = Optional[Union[Union[ModelVolume, _BaseVolume], List[Union[ModelVolume, _BaseVolume]]]]
TContext = TypeVar("TContext", bound="ContextMixin")
THookable = TypeVar("THookable", bound="HookMixin")


class HookMixin(BaseMixin):
    def _dispatch_hooks(self: THookable) -> THookable:
        output = self
        for hook in global_config._get_pre_build_hooks(output):
            output = hook(output)
            if output is None:
                raise RuntimeError(
                    f"Pre-build hook {hook.__name__} returned None."
                    "Please ensure you are returning the output value from the hook."
                )
        return output


class ContextMixin(BaseMixin):
    def __enter__(self: TContext) -> TContext:
        """Enter the context of the workflow"""

        _context.enter(self)
        return self

    def __exit__(self, *_) -> None:
        """Leave the context of the workflow.

        This supports using `with Workflow(...)`.
        """
        _context.exit()

    def _add_sub(self, node: Any) -> Any:
        raise NotImplementedError()


class ContainerMixin(BaseMixin):
    image: Optional[str] = None
    image_pull_policy: Optional[Union[str, ImagePullPolicy]] = None

    liveness_probe: Optional[Probe] = None
    ports: Optional[List[ContainerPort]] = None
    readiness_probe: Optional[Probe] = None
    startup_probe: Optional[Probe] = None
    stdin: Optional[bool] = None
    stdin_once: Optional[bool] = None
    termination_message_path: Optional[str] = None
    termination_message_policy: Optional[TerminationMessagePolicy] = None
    tty: Optional[bool] = None

    def _build_image_pull_policy(self) -> Optional[str]:
        if self.image_pull_policy is None:
            return None
        elif isinstance(self.image_pull_policy, ImagePullPolicy):
            return self.image_pull_policy.value
        return ImagePullPolicy[self.image_pull_policy.lower()].value

    @validator("image", pre=True, always=True)
    def _set_image(cls, v):
        if v is None:
            return global_config.image
        return v


class IOMixin(BaseMixin):
    inputs: InputsT = None
    outputs: OutputsT = None

    def _build_inputs(self) -> Optional[ModelInputs]:
        if self.inputs is None:
            return None
        elif isinstance(self.inputs, ModelInputs):
            return self.inputs

        result = ModelInputs()
        inputs = self.inputs if isinstance(self.inputs, list) else [self.inputs]
        for value in inputs:
            if isinstance(value, dict):
                for k, v in value.items():
                    value = Parameter(name=k, value=v)
                    result.parameters = [value] if result.parameters is None else result.parameters + [value]
            elif isinstance(value, Parameter):
                result.parameters = (
                    [value.as_input()] if result.parameters is None else result.parameters + [value.as_input()]
                )
            elif isinstance(value, ModelParameter):
                result.parameters = [value] if result.parameters is None else result.parameters + [value]
            elif isinstance(value, Artifact):
                result.artifacts = (
                    [value._build_artifact()]
                    if result.artifacts is None
                    else result.artifacts + [value._build_artifact()]
                )
            else:
                result.artifacts = [value] if result.artifacts is None else result.artifacts + [value]

        if result.parameters is None and result.artifacts is None:
            return None
        return result

    def _build_outputs(self) -> Optional[ModelOutputs]:
        if not self.outputs:
            return None
        elif isinstance(self.outputs, ModelOutputs):
            return self.outputs

        result = ModelOutputs()
        outputs = self.outputs if isinstance(self.outputs, list) else [self.outputs]
        for value in outputs:
            if isinstance(value, Parameter):
                result.parameters = (
                    [value.as_output()] if result.parameters is None else result.parameters + [value.as_output()]
                )
            elif isinstance(value, ModelParameter):
                result.parameters = [value] if result.parameters is None else result.parameters + [value]
            elif isinstance(value, Artifact):
                result.artifacts = (
                    [value._build_artifact()]
                    if result.artifacts is None
                    else result.artifacts + [value._build_artifact()]
                )
            else:
                result.artifacts = [value] if result.artifacts is None else result.artifacts + [value]

        if result.parameters is None and result.artifacts is None:
            return None
        return result


class EnvMixin(BaseMixin):
    env: EnvT = None
    env_from: EnvFromT = None

    def _build_env(self) -> Optional[List[EnvVar]]:
        if self.env is None:
            return None

        result: List[EnvVar] = []
        env = self.env if isinstance(self.env, list) else [self.env]
        for e in env:
            if isinstance(e, EnvVar):
                result.append(e)
            elif issubclass(e.__class__, _BaseEnv):
                result.append(e.build())
            elif isinstance(e, dict):
                for k, v in e.items():
                    result.append(EnvVar(name=k, value=v))
        return result

    def _build_env_from(self) -> Optional[List[EnvFromSource]]:
        if self.env_from is None:
            return None

        result: List[EnvFromSource] = []
        env_from = self.env_from if isinstance(self.env_from, list) else [self.env_from]
        for e in env_from:
            if isinstance(e, EnvFromSource):
                result.append(e)
            elif issubclass(e.__class__, _BaseEnvFrom):
                result.append(e.build())
        return result

    def _build_params_from_env(self) -> Optional[List[Parameter]]:
        if self.env is None:
            return None

        params: Optional[List[Parameter]] = None
        for spec in self.env:
            if isinstance(spec, Env) and spec.value_from_input is not None:
                value = (
                    spec.value_from_input.value
                    if isinstance(spec.value_from_input, Parameter)
                    else spec.value_from_input
                )
                params = (
                    [Parameter(name=spec.param_name, value=value)]
                    if params is None
                    else params + [Parameter(name=spec.param_name, value=value)]
                )

        return params


class MetricsMixin(BaseMixin):
    metrics: Optional[
        Union[
            _BaseMetric,
            List[_BaseMetric],
            Metrics,
            ModelPrometheus,
            List[ModelPrometheus],
            ModelMetrics,
        ]
    ] = None

    def _build_metrics(self) -> Optional[ModelMetrics]:
        if self.metrics is None or isinstance(self.metrics, ModelMetrics):
            return self.metrics
        elif isinstance(self.metrics, ModelPrometheus):
            return ModelMetrics(prometheus=[self.metrics])
        elif isinstance(self.metrics, Metrics):
            return ModelMetrics(prometheus=self.metrics._build_metrics())
        elif isinstance(self.metrics, _BaseMetric):
            return ModelMetrics(prometheus=[self.metrics._build_metric()])

        metrics = []
        for m in self.metrics:
            if isinstance(m, _BaseMetric):
                metrics.append(m._build_metric())
            else:
                metrics.append(m)
        return ModelMetrics(prometheus=metrics)


class TemplateMixin(SubNodeMixin, HookMixin, MetricsMixin):
    active_deadline_seconds: Optional[Union[int, str, IntOrString]] = None
    affinity: Optional[Affinity] = None
    archive_location: Optional[ArtifactLocation] = None
    automount_service_account_token: Optional[bool] = None
    daemon: Optional[bool] = None
    executor: Optional[ExecutorConfig] = None
    fail_fast: Optional[bool] = None
    host_aliases: Optional[List[HostAlias]] = None
    init_containers: Optional[List[Union[UserContainer, ModelUserContainer]]] = None
    memoize: Optional[Memoize] = None
    annotations: Optional[Dict[str, str]] = None
    labels: Optional[Dict[str, str]] = None
    name: Optional[str] = None
    node_selector: Optional[Dict[str, str]] = None
    parallelism: Optional[int] = None
    http: Optional[HTTP] = None
    plugin: Optional[Plugin] = None
    pod_spec_patch: Optional[str] = None
    priority: Optional[int] = None
    priority_class_name: Optional[str] = None
    retry_strategy: Optional[RetryStrategy] = None
    scheduler_name: Optional[str] = None
    pod_security_context: Optional[PodSecurityContext] = None
    service_account_name: Optional[str] = None
    sidecars: Optional[Union[UserContainer, List[UserContainer]]] = None
    synchronization: Optional[Synchronization] = None
    timeout: Optional[str] = None
    tolerations: Optional[List[Toleration]] = None

    def _build_sidecars(self) -> Optional[List[UserContainer]]:
        if self.sidecars is None:
            return None

        if isinstance(self.sidecars, UserContainer):
            return [self.sidecars]

        return self.sidecars

    def _build_active_deadline_seconds(self) -> Optional[IntOrString]:
        if self.active_deadline_seconds is None:
            return None

        return IntOrString(__root__=str(self.active_deadline_seconds))

    def _build_metadata(self) -> Optional[Metadata]:
        if self.annotations is None and self.labels is None:
            return None

        return Metadata(
            annotations=self.annotations,
            labels=self.labels,
        )


class ResourceMixin(BaseMixin):
    resources: Optional[Union[ResourceRequirements, Resources]] = None

    def _build_resources(self) -> Optional[ResourceRequirements]:
        if self.resources is None or isinstance(self.resources, ResourceRequirements):
            return self.resources

        return self.resources.build()


class VolumeMixin(BaseMixin):
    volumes: VolumesT = None

    def _build_volumes(self) -> Optional[List[ModelVolume]]:
        if self.volumes is None:
            return None

        volumes = self.volumes if isinstance(self.volumes, list) else [self.volumes]
        # filter volumes for otherwise we're building extra Argo volumes
        filtered_volumes = [v for v in volumes if not isinstance(v, Volume)]
        # only build volumes if there are any of type `_BaseVolume`, otherwise it must be an autogenerated model
        # already, so kept it as it is
        result = [v._build_volume() if issubclass(v.__class__, _BaseVolume) else v for v in filtered_volumes]
        return result or None

    def _build_persistent_volume_claims(self) -> Optional[List[PersistentVolumeClaim]]:
        if self.volumes is None:
            return None

        volumes = self.volumes if isinstance(self.volumes, list) else [self.volumes]
        volumes_with_pv_claims = [v for v in volumes if isinstance(v, Volume)]
        if not volumes_with_pv_claims:
            return None

        claims = [v._build_persistent_volume_claim() for v in volumes_with_pv_claims]
        return claims or None


class VolumeMountMixin(VolumeMixin):
    volume_devices: Optional[List[VolumeDevice]] = None
    volume_mounts: Optional[List[VolumeMount]] = None

    def _build_volume_mounts(self) -> Optional[List[VolumeMount]]:
        # while it's possible for `volume_mounts` to be `None`, this has to check that `volumes` is also `None` since
        # it's possible that Hera can find volume mounts to generate for the user if there are any volumes set
        if self.volume_mounts is None and self.volumes is None:
            return None

        if isinstance(self.volumes, list):
            volumes = self.volumes
        elif not isinstance(self.volumes, list) and self.volumes is not None:
            volumes = [self.volumes]
        else:
            volumes = []

        result = (
            None
            if self.volumes is None
            else [v._build_volume_mount() if issubclass(v.__class__, _BaseVolume) else v for v in volumes]
        )
        if result is None and self.volume_mounts is None:
            return None
        elif result is None and self.volume_mounts is not None:
            return self.volume_mounts

        mounts = cast(List[VolumeMount], self.volume_mounts) or [] + cast(List[VolumeMount], result) or []
        return mounts or None


class ArgumentsMixin(BaseMixin):
    arguments: ArgumentsT = None

    def _build_arguments(self) -> Optional[ModelArguments]:
        if self.arguments is None:
            return None
        elif isinstance(self.arguments, ModelArguments):
            return self.arguments

        result = ModelArguments()
        arguments = self.arguments if isinstance(self.arguments, list) else [self.arguments]
        for arg in arguments:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    value = Parameter(name=k, value=v)
                    result.parameters = [value] if result.parameters is None else result.parameters + [value]
            elif isinstance(arg, ModelArtifact):
                result.artifacts = [arg] if result.artifacts is None else result.artifacts + [arg]
            elif isinstance(arg, Artifact):
                result.artifacts = (
                    [arg._build_artifact()] if result.artifacts is None else result.artifacts + [arg._build_artifact()]
                )
            elif isinstance(arg, ModelParameter):
                result.parameters = [arg] if result.parameters is None else result.parameters + [arg]
            elif isinstance(arg, Parameter):
                result.parameters = (
                    [arg.as_argument()] if result.parameters is None else result.parameters + [arg.as_argument()]
                )

        if result.parameters is None and result.artifacts is None:
            return None
        return result


class CallableTemplateMixin(ArgumentsMixin):
    def __call__(self, *args, **kwargs) -> Union[Step, Task]:
        if "name" not in kwargs:
            kwargs["name"] = self.name  # type: ignore

        # when the `source` is set via an `@script` decorator, it does not come in with the `kwargs` so we need to
        # set it here in order for the following logic to capture it
        if "source" not in kwargs and hasattr(self, "source"):
            kwargs["source"] = self.source  # type: ignore

        try:
            from hera.workflows.steps import Step

            return Step(*args, template=self, **kwargs)
        except InvalidType:
            pass

        try:
            from hera.workflows.task import Task

            arguments = self._get_arguments(**kwargs)
            parameter_names = self._get_parameter_names(arguments)
            artifact_names = self._get_artifact_names(arguments)
            if "source" in kwargs and "with_param" in kwargs:
                arguments += self._get_deduped_params_from_source(parameter_names, artifact_names, kwargs["source"])
            elif "source" in kwargs and "with_items" in kwargs:
                arguments += self._get_deduped_params_from_items(parameter_names, kwargs["with_items"])

            # it is possible for the user to pass `arguments` via `kwargs` along with `with_param`. The `with_param`
            # additional parameters are inferred and have to be added to the `kwargs['arguments']` for otherwise
            # the task will miss adding them when building the final arguments
            kwargs["arguments"] = arguments

            return Task(*args, template=self, **kwargs)
        except InvalidType:
            pass

        raise InvalidTemplateCall("Container is not under a Steps, Parallel, or DAG context")

    def _get_arguments(self, **kwargs) -> List:
        """Returns a list of arguments from the kwargs given to the template call"""

        # these are the already set parameters. If a user has already set a parameter argument, then Hera
        # uses the user-provided value rather than the inferred value
        kwargs_arguments = kwargs.get("arguments", [])
        kwargs_arguments = (
            kwargs_arguments if isinstance(kwargs_arguments, List) else [kwargs_arguments]
        )  # type: ignore
        arguments = (
            self.arguments if isinstance(self.arguments, List) else [self.arguments] + kwargs_arguments
        )  # type: ignore
        return list(filter(lambda x: x is not None, arguments))

    def _get_parameter_names(self, arguments: List) -> Set[str]:
        parameters = [arg for arg in arguments if isinstance(arg, ModelParameter) or isinstance(arg, Parameter)]
        return {p.name for p in parameters}

    def _get_artifact_names(self, arguments: List) -> Set[str]:
        artifacts = [arg for arg in arguments if isinstance(arg, ModelArtifact) or isinstance(arg, Artifact)]
        return {a.name for a in artifacts}

    def _get_deduped_params_from_source(
        self, parameter_names: Set[str], artifact_names: Set[str], source: Callable
    ) -> List[Parameter]:
        """Infer arguments from the given source and deduplicates based on the given params and artifacts.

        Argo uses the `inputs` field to indicate the expected parameters of a specific template whereas the
        `arguments` are used to indicate exactly what _values_ are assigned to the set inputs. Here,
        we infer the arguments when `with_param` is used. If a source is passed along with `with_param`, we
        infer the arguments to set from the given source. It is assumed that `with_param` will return the
        expected result for Argo to fan out the task on.

        Parameters
        ----------
        parameter_names: Set[str]
            Set of already constructed parameter names.
        artifact_names: Set[str]
            Set of already constructed artifact names.
        source: Callable
            The source function to infer the arguments from.

        Returns
        -------
        List[Parameter]
            The list of inferred arguments to set.
        """
        new_arguments = []
        new_parameters = _get_params_from_source(source)
        if new_parameters is not None:
            for p in new_parameters:
                if p.name not in parameter_names and p.name not in artifact_names:
                    new_arguments.append(p)
        return new_arguments

    def _get_deduped_params_from_items(self, parameter_names: Set[str], items: List[Any]) -> List[Parameter]:
        """Infer arguments from the given items.

        The main difference between `with_items` and `with_param` is that param is a serialized version of
        `with_items`. Hence, `with_items` comes in the form of a list of objects, whereas `with_param` comes
        in as a single serialized object. Here, we can infer the parameters to create based on the content
        of `with_items`.

        Parameters
        ----------
        parameter_names: Set[str]
            Set of already constructed parameter names.
        items: List[Any]
            The items to infer the arguments from.

        Returns
        -------
        List[Parameter]
            The list of inferred arguments to set.
        """
        item_params = _get_params_from_items(items)
        new_params = []
        if item_params is not None:
            for p in item_params:
                if p.name not in parameter_names:
                    new_params.append(p)
        return new_params


class ParameterMixin(BaseMixin):
    with_param: Optional[Any] = None  # this must be a serializable object, or `hera.workflows.parameter.Parameter`

    def _build_with_param(self) -> Optional[str]:
        if self.with_param is None:
            return None

        if isinstance(self.with_param, Parameter):
            return self.with_param.value
        elif isinstance(self.with_param, str):
            return self.with_param
        return serialize(self.with_param)


class ItemMixin(BaseMixin):
    with_items: Optional[List[Any]] = None  # this must composed of serializable objects

    def _build_with_items(self) -> Optional[List[Item]]:
        if self.with_items is None:
            return None

        if isinstance(self.with_items, list):
            items = []
            for item in self.with_items:
                if isinstance(item, Parameter):
                    items.append(Item(__root__=item.value))
                elif (
                    isinstance(item, str) or isinstance(item, dict) or isinstance(item, float) or isinstance(item, int)
                ):
                    items.append(Item(__root__=item))
                elif isinstance(item, Item):
                    items.append(item)
                else:
                    items.append(Item(__root__=serialize(item)))
            return items
        elif isinstance(self.with_items, Parameter):
            return [Item(__root__=self.with_items.value)]
        elif isinstance(self.with_items, str):
            return [Item(__root__=self.with_items)]
        return [Item(__root__=serialize(self.with_items))]


class EnvIOMixin(EnvMixin, IOMixin):
    def _build_inputs(self) -> Optional[ModelInputs]:
        inputs = super()._build_inputs()
        env_params = self._build_params_from_env()
        if inputs is None and env_params is None:
            return None
        elif inputs is None:
            return ModelInputs(parameters=env_params)
        elif env_params is None:
            return inputs

        # at this stage we know that they are both defined, so we have to join them. One thing to be aware of is that
        # the user might have already set the env parameters in the inputs, so we need to check for that
        if inputs.parameters is None:
            return inputs

        already_set_params = {p.name for p in inputs.parameters or []}
        for param in env_params:
            if param.name not in already_set_params:
                inputs.parameters = [param] if inputs.parameters is None else inputs.parameters + [param]
        return inputs


class TemplateInvocatorSubNodeMixin(BaseMixin):
    """Used for classes that form sub nodes of Template Invocators - "Steps" and "DAG".

    See https://argoproj.github.io/argo-workflows/workflow-concepts/#template-invocators for
    more on template invocators
    """

    name: str
    continue_on: Optional[ContinueOn] = None
    hooks: Optional[Dict[str, LifecycleHook]] = None
    on_exit: Optional[Union[str, Templatable]] = None
    template: Optional[Union[str, Template, TemplateMixin]] = None
    template_ref: Optional[TemplateRef] = None
    inline: Optional[Union[Template, TemplateMixin]] = None
    when: Optional[str] = None
    with_sequence: Optional[Sequence] = None

    def _build_on_exit(self) -> Optional[str]:
        if isinstance(self.on_exit, Templatable):
            return self.on_exit._build_template().name  # type: ignore
        return self.on_exit

    @property
    def _subtype(self) -> str:
        raise NotImplementedError

    @property
    def id(self) -> str:
        """ID of this node."""
        return f"{{{{{self._subtype}.{self.name}.id}}}}"

    @property
    def ip(self) -> str:
        """IP of this node."""
        return f"{{{{{self._subtype}.{self.name}.ip}}}}"

    @property
    def status(self) -> str:
        """Status of this node."""
        return f"{{{{{self._subtype}.{self.name}.status}}}}"

    @property
    def exit_code(self) -> str:
        """ExitCode holds the exit code of a script template."""
        return f"{{{{{self._subtype}.{self.name}.exitCode}}}}"

    @property
    def started_at(self) -> str:
        """Time at which this node started."""
        return f"{{{{{self._subtype}.{self.name}.startedAt}}}}"

    @property
    def finished_at(self) -> str:
        """Time at which this node completed."""
        return f"{{{{{self._subtype}.{self.name}.finishedAt}}}}"

    @property
    def result(self) -> str:
        """Result holds the result (stdout) of a script template."""
        return f"{{{{{self._subtype}.{self.name}.outputs.result}}}}"

    def get_result_as(self, name: str) -> Parameter:
        return Parameter(name=name, value=self.result)

    @root_validator(pre=False)
    def _check_values(cls, values):
        def one(xs: List):
            xs = list(map(bool, xs))
            return xs.count(True) == 1

        if not one([values.get("template"), values.get("template_ref"), values.get("inline")]):
            raise ValueError("exactly one of ['template', 'template_ref', 'inline'] must be present")
        return values

    def _get_parameters_as(self, name: str, subtype: str) -> Parameter:
        """Returns a `Parameter` that represents all the outputs of the specified subtype.

        Parameters
        ----------
        name: str
            The name of the parameter to search for.
        subtype: str
            The inheritor subtype field, used to construct the output artifact `from_` reference.

        Returns
        -------
        Parameter
            The parameter, named based on the given `name`, along with a value that references all outputs.
        """
        return Parameter(name=name, value=f"{{{{{subtype}.{self.name}.outputs.parameters}}}}")

    def _get_parameter(self, name: str, subtype: str) -> Parameter:
        """Attempts to find the specified parameter in the outputs for the specified subtype.

        Notes
        -----
        This is specifically designed to be invoked by inheritors.

        Parameters
        ----------
        name: str
            The name of the parameter to search for.
        subtype: str
            The inheritor subtype field, used to construct the output artifact `from_` reference.

        Returns
        -------
        Parameter
            The parameter if found.

        Raises
        ------
        ValueError
            When no outputs can be constructed/no outputs are set.
        KeyError
            When the artifact is not found.
        NotImplementedError
            When something else other than an `Parameter` is found for the specified name.
        """
        if isinstance(self.template, str):
            raise ValueError(f"Cannot get output parameters when the template was set via a name: {self.template}")

        # here, we build the template early to verify that we can get the outputs
        if isinstance(self.template, Templatable):
            template = self.template._build_template()
        else:
            template = self.template

        # at this point, we know that the template is a `Template` object
        if template.outputs is None:  # type: ignore
            raise ValueError(f"Cannot get output parameters when the template has no outputs: {template}")
        if template.outputs.parameters is None:  # type: ignore
            raise ValueError(f"Cannot get output parameters when the template has no output parameters: {template}")
        parameters = template.outputs.parameters  # type: ignore

        obj = next((output for output in parameters if output.name == name), None)
        if obj is not None:
            return Parameter(
                name=obj.name,
                value=f"{{{{{subtype}.{self.name}.outputs.parameters.{name}}}}}",
            )
        raise KeyError(f"No output parameter named `{name}` found")

    def _get_artifact(self, name: str, subtype: str) -> Artifact:
        """Attempts to find the specified artifact in the outputs for the specified subtype.

        Notes
        -----
        This is specifically designed to be invoked by inheritors.

        Parameters
        ----------
        name: str
            The name of the artifact to search for.
        subtype: str
            The inheritor subtype field, used to construct the output artifact `from_` reference.

        Returns
        -------
        Artifact
            The artifact if found.

        Raises
        ------
        ValueError
            When no outputs can be constructed/no outputs are set.
        KeyError
            When the artifact is not found.
        NotImplementedError
            When something else other than an `Artifact` is found for the specified name.
        """
        if isinstance(self.template, str):
            raise ValueError(f"Cannot get output parameters when the template was set via a name: {self.template}")

        # here, we build the template early to verify that we can get the outputs
        if isinstance(self.template, Templatable):
            template = self.template._build_template()
        else:
            template = cast(Template, self.template)

        # at this point, we know that the template is a `Template` object
        if template.outputs is None:  # type: ignore
            raise ValueError(f"Cannot get output artifacts when the template has no outputs: {template}")
        elif template.outputs.artifacts is None:  # type: ignore
            raise ValueError(f"Cannot get output artifacts when the template has no output artifacts: {template}")
        artifacts = cast(List[ModelArtifact], template.outputs.artifacts)

        obj = next((output for output in artifacts if output.name == name), None)
        if obj is not None:
            return Artifact(name=name, path=obj.path, from_=f"{{{{{subtype}.{self.name}.outputs.artifacts.{name}}}}}")
        raise KeyError(f"No output artifact named `{name}` found")

    def get_parameters_as(self, name: str) -> Parameter:
        """Returns a `Parameter` that represents all the outputs of this subnode.

        Parameters
        ----------
        name: str
            The name of the parameter to search for.

        Returns
        -------
        Parameter
            The parameter, named based on the given `name`, along with a value that references all outputs.
        """
        return self._get_parameters_as(name=name, subtype=self._subtype)

    def get_artifact(self, name: str) -> Artifact:
        """Gets an artifact from the outputs of this subnode"""
        return self._get_artifact(name=name, subtype=self._subtype)

    def get_parameter(self, name: str) -> Parameter:
        """Gets a parameter from the outputs of this subnode"""
        return self._get_parameter(name=name, subtype=self._subtype)


def _get_params_from_source(source: Callable) -> Optional[List[Parameter]]:
    source_signature: Dict[str, Optional[object]] = {}
    for p in inspect.signature(source).parameters.values():
        if p.default != inspect.Parameter.empty and p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            source_signature[p.name] = p.default
        else:
            source_signature[p.name] = MISSING

    if len(source_signature) == 0:
        return None
    elif len(source_signature) == 1:
        return [Parameter(name=n, value="{{item}}") for n in source_signature.keys()]
    return [Parameter(name=n, value=f"{{{{item.{n}}}}}") for n in source_signature.keys()]


def _get_params_from_items(with_items: List[Any]) -> Optional[List[Parameter]]:
    if len(with_items) == 0:
        return None
    elif len(with_items) == 1:
        el = with_items[0]
        if len(el.keys()) == 1:
            return [Parameter(name=n, value="{{item}}") for n in el.keys()]
        else:
            return [Parameter(name=n, value=f"{{{{item.{n}}}}}") for n in el.keys()]
    return [Parameter(name=n, value=f"{{{{item.{n}}}}}") for n in with_items[0].keys()]


class ExperimentalMixin(BaseMixin):
    _experimental_warning_message: str = (
        "Unable to instantiate {} since it is an experimental feature."
        ' Please turn on experimental features by setting `hera.shared.global_config.experimental_features["{}"] = True`.'
        " Note that experimental features are unstable and subject to breaking changes."
    )

    _flag: str

    @root_validator
    def _check_enabled(cls, values):
        if not global_config.experimental_features[cls._flag]:
            raise ValueError(cls._experimental_warning_message.format(cls, cls._flag))
        return values
