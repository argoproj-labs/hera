"""Core collection of Hera mixins that isolate shareable functionality between Hera objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Sequence as SequenceType,
    TypeVar,
    Union,
    cast,
)

from hera.shared import BaseMixin, global_config
from hera.shared._pydantic import get_field_annotations, get_fields
from hera.shared._type_util import construct_io_from_annotation
from hera.shared.serialization import serialize
from hera.workflows._context import SubNodeMixin, _context
from hera.workflows._meta_mixins import HeraBuildObj, HookMixin
from hera.workflows.artifact import Artifact
from hera.workflows.env import Env, _BaseEnv
from hera.workflows.env_from import _BaseEnvFrom
from hera.workflows.metrics import Metrics, _BaseMetric
from hera.workflows.models import (
    Affinity,
    Arguments as ModelArguments,
    Artifact as ModelArtifact,
    ArtifactLocation,
    ContainerPort,
    ContainerResizePolicy,
    ContinueOn,
    EnvFromSource,
    EnvVar,
    ExecutorConfig,
    HostAlias,
    ImagePullPolicy,
    Inputs as ModelInputs,
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
    RetryStrategy as ModelRetryStrategy,
    Sequence,
    Synchronization,
    Template,
    TemplateRef,
    Toleration,
    UserContainer as ModelUserContainer,
    Volume as ModelVolume,
    VolumeDevice,
    VolumeMount,
)
from hera.workflows.parameter import Parameter
from hera.workflows.protocol import Templatable
from hera.workflows.resources import Resources
from hera.workflows.retry_strategy import RetryStrategy
from hera.workflows.user_container import UserContainer
from hera.workflows.volume import Volume, _BaseVolume

T = TypeVar("T")
OneOrMany = Union[T, SequenceType[T]]
"""OneOrMany is provided as a convenience type to allow Hera models to accept single values or lists (sequences) of
values, and so that our code is more readable."""


def normalize_to_list(v: OneOrMany) -> List:
    """Normalize given value to a list if not None."""
    if isinstance(v, list):
        return v
    return [v]


InputsT = Optional[
    Union[
        ModelInputs,
        OneOrMany[Union[Parameter, ModelParameter, Artifact, ModelArtifact, Dict[str, Any]]],
    ]
]
"""`InputsT` is the main type associated with inputs that can be specified in Hera workflows, dags, steps, etc.

This type enables uses of Hera auto-generated models such as (`hera.workflows.models.Inputs`,
`hera.workflows.models.Parameter`), Hera managed models such as (`hera.workflows.Parameter`,
`hera.workflows.Artifact`), dictionary mappings of parameter names to values (auto-converted by Hera to
`hera.workflows.Parameter`), or lists of any of the aforementioned objects.
"""

OutputsT = Optional[
    Union[
        ModelOutputs,
        OneOrMany[Union[Parameter, ModelParameter, Artifact, ModelArtifact]],
    ]
]
"""`OutputsT` is the main type associated with outputs the can be specified in Hera workflows, dags, steps, etc.

This type enables uses of Hera auto-generated models such as (`hera.workflows.models.Outputs`,
`hera.workflows.models.Parameter`), Hera managed models such as (`hera.workflows.Parameter`,
`hera.workflows.Artifact`),  or lists of the aforementioned objects.
"""

ArgumentsT = Optional[
    Union[
        ModelArguments,
        OneOrMany[Union[Parameter, ModelParameter, Artifact, ModelArtifact, Dict[str, Any]]],
        ModelOutputs,
    ]
]
"""`ArgumentsT` is the main type associated with arguments that can be used on DAG tasks, steps, etc.

This type enables uses of the Hera auto-generated `hera.workflows.models.Arguments` model, Hera managed models such as
`hera.workflows.Parameter`, `hera.workflows.Artifact`, a dictionary mapping of parameter names to values, or a list of
any of the aforementioned objects.
"""

MetricsT = Optional[
    Union[
        Metrics,
        ModelMetrics,
        OneOrMany[_BaseMetric],
        OneOrMany[ModelPrometheus],
    ]
]
"""`MetricsT` is the core Hera type for Prometheus metrics.

This metrics type enables users to use either auto-generated Hera metrics, lists of auto-generated single metrics, or
the variations of metrics provided by `hera.workflows.metrics.*`
"""

EnvT = Optional[OneOrMany[Union[_BaseEnv, EnvVar, Dict[str, Any]]]]
"""`EnvT` is the core Hera type for environment variables.

The env type enables setting single valued environment variables, lists of environment variables, or dictionary
mappings of env variables names to values, which are automatically parsed by Hera.
"""

EnvFromT = Optional[OneOrMany[Union[_BaseEnvFrom, EnvFromSource]]]
"""`EnvFromT` is the core Hera type for environment variables derived from Argo/Kubernetes sources.

This env type enables specifying environment variables in base form, as `hera.workflows.env` form, or lists of the
aforementioned objects.
"""

VolumesT = Optional[OneOrMany[Union[ModelVolume, _BaseVolume]]]
"""`VolumesT` is the core Hera type for volumes.

This volume type is used to specify the configuration of volumes to be automatically created by Argo/K8s and mounted
by Hera at specific mount paths in containers.
"""


@dataclass(kw_only=True)
class ContainerMixin(BaseMixin):
    """`ContainerMixin` provides a subset of the fields of a container such as image, probes, etc."""

    image: Optional[str] = None
    image_pull_policy: Optional[Union[str, ImagePullPolicy]] = None

    liveness_probe: Optional[Probe] = None
    ports: Optional[List[ContainerPort]] = None
    readiness_probe: Optional[Probe] = None
    startup_probe: Optional[Probe] = None
    stdin: Optional[bool] = None
    stdin_once: Optional[bool] = None
    termination_message_path: Optional[str] = None
    termination_message_policy: Optional[str] = None
    tty: Optional[bool] = None

    def __post_init__(self):
        """Validate image field. Set to the global image if None."""
        super().__post_init__()

        if self.image is None:
            self.image = global_config.image

    def _build_image_pull_policy(self) -> Optional[str]:
        """Processes the image pull policy field and returns a generated `ImagePullPolicy` enum."""
        if self.image_pull_policy is None:
            return None
        elif isinstance(self.image_pull_policy, ImagePullPolicy):
            return self.image_pull_policy.value

        # this helps map image pull policy values as a convenience
        policy_mapper = {
            # the following 2 are "normal" entries
            **{ipp.name: ipp for ipp in ImagePullPolicy},
            **{ipp.value: ipp for ipp in ImagePullPolicy},
            # some users might submit the policy without underscores
            **{ipp.value.lower().replace("_", ""): ipp for ipp in ImagePullPolicy},
            # some users might submit the policy in lowercase
            **{ipp.name.lower(): ipp for ipp in ImagePullPolicy},
        }
        try:
            return ImagePullPolicy[policy_mapper[self.image_pull_policy].name].value
        except KeyError as e:
            raise KeyError(
                f"Supplied image policy {self.image_pull_policy} is not valid. "
                "Use one of {ImagePullPolicy.__members__}"
            ) from e


@dataclass(kw_only=True)
class IOMixin(BaseMixin):
    """`IOMixin` provides the capabilities of performing I/O between steps via fields such as `inputs`/`outputs`."""

    inputs: InputsT = None
    outputs: OutputsT = None

    def get_parameter(self, name: str) -> Parameter:
        """Finds and returns the parameter with the supplied name.

        Note that this method will raise an error if the parameter is not found.

        Args:
            name: name of the input parameter to find and return.

        Returns:
            Parameter: the parameter with the supplied name.

        Raises:
            KeyError: if the parameter is not found.
        """
        inputs = self._build_inputs()
        if inputs is None:
            raise KeyError(f"No inputs set. Parameter {name} not found.")
        if inputs.parameters is None:
            raise KeyError(f"No parameters set. Parameter {name} not found.")
        for p in inputs.parameters:
            if p.name == name:
                param = Parameter.from_model(p)
                param.value = f"{{{{inputs.parameters.{param.name}}}}}"
                return param
        raise KeyError(f"Parameter {name} not found.")

    def get_artifact(self, name: str) -> Artifact:
        """Finds and returns the artifact with the supplied name.

        Note that this method will raise an error if the artifact is not found.

        Args:
            name: name of the input artifact to find and return.

        Returns:
            Artifact: the artifact with the supplied name.

        Raises:
            KeyError: if the artifact is not found.
        """
        inputs = self._build_inputs()
        if inputs is None:
            raise KeyError(f"No inputs set. Artifact {name} not found.")
        if inputs.artifacts is None:
            raise KeyError(f"No artifacts set. Artifact {name} not found.")
        for artifact in inputs.artifacts:
            if artifact.name == name:
                return Artifact(name=name, from_=f"{{{{inputs.artifacts.{artifact.name}}}}}")
        raise KeyError(f"Artifact {name} not found.")

    def _build_inputs(self) -> Optional[ModelInputs]:
        """Processes the `inputs` field and returns a generated `ModelInputs`."""
        if self.inputs is None:
            return None
        elif isinstance(self.inputs, ModelInputs):
            return self.inputs

        result = ModelInputs()
        for value in normalize_to_list(self.inputs):
            if isinstance(value, dict):
                for k, v in value.items():
                    value = ModelParameter(name=k, value=v)
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
            elif isinstance(value, ModelArtifact):
                result.artifacts = [value] if result.artifacts is None else result.artifacts + [value]
            else:
                raise ValueError(f"Unrecognised type {type(value)} for input value {value}")

        # returning `None` for `ModelInputs` means the submission to the server will not even have the `inputs` field
        # set, which saves some space
        if result.parameters is None and result.artifacts is None:
            return None
        return result

    def _build_outputs(self) -> Optional[ModelOutputs]:
        """Processes the `outputs` field and returns a generated `ModelOutputs`."""
        if not self.outputs:
            return None
        elif isinstance(self.outputs, ModelOutputs):
            # Special case as Parameter is a subclass of ModelParameter
            # We need to convert Parameters to ModelParameters
            return self.outputs

        result = ModelOutputs()
        for value in normalize_to_list(self.outputs):
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
            elif isinstance(value, ModelArtifact):
                result.artifacts = [value] if result.artifacts is None else result.artifacts + [value]

        # returning `None` for `ModelInputs` means the submission to the server will not even have the `outputs` field
        # set, which saves some space
        if result.parameters is None and result.artifacts is None:
            return None
        return result


@dataclass(kw_only=True)
class EnvMixin(BaseMixin):
    """`EnvMixin` provides the ability to set simple env variables along with env variables that are derived."""

    env: EnvT = None
    env_from: EnvFromT = None

    def _build_env(self) -> Optional[List[EnvVar]]:
        """Processes the `env` field and returns a list of generated `EnvVar` or `None`."""
        if self.env is None:
            return None

        result: List[EnvVar] = []
        for e in normalize_to_list(self.env):
            if isinstance(e, EnvVar):
                result.append(e)
            elif issubclass(e.__class__, _BaseEnv):
                result.append(e.build())  # type: ignore
            elif isinstance(e, dict):
                for k, v in e.items():
                    result.append(EnvVar(name=k, value=str(v)))

        # returning `None` for `envs` means the submission to the server will not even have the `envs` field
        # set, which saves some space
        return result if result else None

    def _build_env_from(self) -> Optional[List[EnvFromSource]]:
        """Processes the `env_from` field and returns a list of generated `EnvFrom` or `None`."""
        if self.env_from is None:
            return None

        result: List[EnvFromSource] = []
        for e in normalize_to_list(self.env_from):
            if isinstance(e, EnvFromSource):
                result.append(e)
            elif issubclass(e.__class__, _BaseEnvFrom):
                result.append(e.build())  # type: ignore

        # returning `None` for `envs` means the submission to the server will not even have the `env_from` field
        # set, which saves some space
        return result if result else None


@dataclass(kw_only=True)
class MetricsMixin(BaseMixin):
    """`MetricsMixin` provides the ability to set metrics on a n object."""

    metrics: Optional[MetricsT] = None

    def _build_metrics(self) -> Optional[ModelMetrics]:
        """Processes the `metrics` field and returns the generated `ModelMetrics` or `None`."""
        if self.metrics is None or isinstance(self.metrics, ModelMetrics):
            return self.metrics
        elif isinstance(self.metrics, Metrics):
            return ModelMetrics(prometheus=self.metrics._build_metrics())

        metrics = []
        for m in normalize_to_list(self.metrics):
            if isinstance(m, _BaseMetric):
                metrics.append(m._build_metric())
            elif isinstance(m, ModelPrometheus):
                metrics.append(m)
        return ModelMetrics(prometheus=metrics) if metrics else None


@dataclass(kw_only=True)
class TemplateMixin(SubNodeMixin, HookMixin, MetricsMixin):
    """`TemplateMixin` provides the Argo template fields that are shared between different sub-template fields.

    The supported sub-template fields are `Script`, `Data`, `DAG`, `Resource`, `Container`, `ContainerSet`, etc.
    """

    active_deadline_seconds: Optional[int | str] = None
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
    plugin: Optional[Plugin] = None
    pod_spec_patch: Optional[str] = None
    priority_class_name: Optional[str] = None
    retry_strategy: Optional[Union[RetryStrategy, ModelRetryStrategy]] = None
    scheduler_name: Optional[str] = None
    pod_security_context: Optional[PodSecurityContext] = None
    service_account_name: Optional[str] = None
    sidecars: Optional[OneOrMany[UserContainer | ModelUserContainer]] = None
    synchronization: Optional[Synchronization] = None
    timeout: Optional[str] = None
    tolerations: Optional[List[Toleration]] = None

    def __post_init__(self) -> None:
        super().__post_init__()

    def _build_init_containers(self) -> Optional[List[ModelUserContainer]]:
        """Builds the `init_containers` field and optionally returns a list of `UserContainer`."""
        if self.init_containers is None:
            return None

        return [i.build() if isinstance(i, UserContainer) else i for i in self.init_containers]

    def _build_sidecars(self) -> Optional[List[ModelUserContainer]]:
        """Builds the `sidecars` field and optionally returns a list of `UserContainer`."""
        if self.sidecars is None:
            return None

        if isinstance(self.sidecars, UserContainer):
            return [self.sidecars.build()]

        result = []
        for s in self.sidecars:
            if isinstance(s, ModelUserContainer):
                result.append(s)
            elif isinstance(s, UserContainer):
                result.append(s.build())

        return result

    def _build_metadata(self) -> Optional[Metadata]:
        """Builds the `metadata` field of the template since the `annotations` and `labels` fields are separated."""
        if self.annotations is None and self.labels is None:
            return None

        return Metadata(
            annotations=self.annotations,
            labels=self.labels,
        )

    def _build_retry_strategy(self) -> Optional[ModelRetryStrategy]:
        if self.retry_strategy is None:
            return None

        if isinstance(self.retry_strategy, RetryStrategy):
            return self.retry_strategy.build()

        return self.retry_strategy


@dataclass(kw_only=True)
class ResourceMixin(BaseMixin):
    """`ResourceMixin` provides the capability to set resources such as compute requirements like CPU, GPU, etc."""

    resources: Optional[Union[ResourceRequirements, Resources]] = None
    resize_policy: Optional[List[ContainerResizePolicy]] = None
    restart_policy: Optional[str] = None

    def _build_resources(self) -> Optional[ResourceRequirements]:
        """Parses the resources and returns a generated `ResourceRequirements` object."""
        if self.resources is None or isinstance(self.resources, ResourceRequirements):
            return self.resources
        return self.resources.build()


# Workflows can use VolumeMixin to create PVCs or specify volume sources (but never mount volumes).
# Containers/scripts use VolumeMountMixin to create PVCs, mount volumes to the container, or specify volume sources.
@dataclass(kw_only=True)
class VolumeMixin(BaseMixin):
    """`VolumeMixin` provides the ability to set volumes on an inheriting resource.

    Note that *any* volumes set on the `volumes` field automatically get an associated persistent volume claim
    constructed and set on the workflow. This way users do not have to set the PVC themselves. However, clients of the
    mixin should be careful to *not* generate multiple PVCs for the same volume.
    """

    volumes: Optional[VolumesT] = None

    def _build_volumes(self) -> Optional[List[ModelVolume]]:
        """Processes the `volumes` and creates an optional list of generated model `Volume`s."""
        if self.volumes is None:
            return None

        # filter volumes to _BaseVolumes or ModelVolumes, otherwise we're building extra Argo volumes from Hera volumes
        filtered_volumes = [v for v in normalize_to_list(self.volumes) if not isinstance(v, Volume)]
        result = [v._build_volume() if isinstance(v, _BaseVolume) else v for v in filtered_volumes]
        return result or None

    def _build_persistent_volume_claims(self) -> Optional[List[PersistentVolumeClaim]]:
        """Generates the list of persistent volume claims to associate with the set `volumes`."""
        if self.volumes is None:
            return None

        volumes_with_pv_claims = [v for v in normalize_to_list(self.volumes) if isinstance(v, Volume)]
        if not volumes_with_pv_claims:
            return None
        return [v._build_persistent_volume_claim() for v in volumes_with_pv_claims] or None


@dataclass(kw_only=True)
class VolumeMountMixin(VolumeMixin):
    """`VolumeMountMixin` supports setting `volume_devices` and `volume_mounts` on the inheritor.

    Devices and mounts are approaches for mounting existing volume resources from a cluster on the job that is
    created via inheriting from this mixin.
    """

    volume_devices: Optional[List[VolumeDevice]] = None
    volume_mounts: Optional[List[VolumeMount]] = None

    def _build_volume_mounts(self) -> Optional[List[VolumeMount]]:
        """Processes the `volumes` and `volume_mounts` fields to generate an optional list of `VolumeMount`s."""
        # We must also check `volumes` is `None` as we generate volume mounts from Hera "Volumes" (subclasses of _BaseVolume)
        if self.volume_mounts is None and self.volumes is None:
            return None

        if self.volumes is None:
            volumes: list = []
        else:
            volumes = normalize_to_list(self.volumes)

        # Users should only use a Hera Volume (with no volume mount) to take advantage of this auto-generation
        generated_volume_mounts = [v._build_volume_mount() for v in volumes if isinstance(v, _BaseVolume)]

        if not generated_volume_mounts and self.volume_mounts is None:
            return None

        return (self.volume_mounts or []) + generated_volume_mounts


@dataclass(kw_only=True)
class ArgumentsMixin(BaseMixin):
    """`ArgumentsMixin` provides the ability to set the `arguments` field on the inheriting object (only Tasks, Steps and Workflows use arguments)."""

    arguments: ArgumentsT = None

    def _build_arguments(self) -> Optional[ModelArguments]:
        """Processes the `arguments` field and builds the optional generated `Arguments` to set as arguments."""
        if self.arguments is None:
            return None

        if isinstance(self.arguments, ModelArguments):
            return self.arguments

        from hera.workflows.workflow_template import WorkflowTemplate

        def add_argument(k: str, v: Any, result: ModelArguments):
            is_workflow_template = isinstance(self, WorkflowTemplate)

            if isinstance(v, Parameter):
                param_copy = v.with_name(k)
                param_as_argument = param_copy.as_input() if is_workflow_template else param_copy.as_argument()
                result.parameters = (result.parameters or []) + [param_as_argument]
            elif isinstance(v, ModelParameter):
                param_copy = Parameter.from_model(v).with_name(k)
                param_as_argument = param_copy.as_input() if is_workflow_template else param_copy.as_argument()
                result.parameters = (result.parameters or []) + [param_as_argument]
            elif isinstance(v, ModelArtifact):
                artifact = v.model_copy(deep=True)
                artifact.name = k
                result.artifacts = (result.artifacts or []) + [artifact]
            elif isinstance(v, Artifact):
                artifact = v.with_name(k)._build_artifact()
                result.artifacts = (result.artifacts or []) + [artifact]
            else:
                # Primitive types are assumed to be parameters, which will be serialised upon creation
                parameter = Parameter(name=k, value=v)
                param_as_argument = parameter.as_input() if is_workflow_template else parameter.as_argument()
                result.parameters = (result.parameters or []) + [param_as_argument]

        result = ModelArguments()
        for arg in normalize_to_list(self.arguments):
            if isinstance(arg, dict):
                for k, v in arg.items():
                    add_argument(k, v, result)
            elif isinstance(arg, (Parameter, ModelParameter, Artifact, ModelArtifact)):
                # name can only be None for Parameters/Artifacts if they have not been
                # "built" yet (see the `_check_name` function)
                add_argument(arg.name or "", arg, result)
            else:
                # Unreachable code (unless model validation is overridden)
                raise TypeError(f"Invalid argument type {type(arg)}")

        # returning `None` for `Arguments` means the submission to the server will not even have the
        # `arguments` field set, which saves some payload
        if result.parameters is None and result.artifacts is None:
            return None
        return result


@dataclass(kw_only=True)
class WithParamMixin(BaseMixin):
    """`ParameterMixin` supports the usage of `with_param` on inheritors."""

    with_param: Optional[Any] = None  # this must be a serializable object, or `hera.workflows.parameter.Parameter`

    def _build_with_param(self) -> Optional[str]:
        """Build the `with_param` field and returns the corresponding `str`.

        The string encodes what to parallelize a process over.
        """
        if self.with_param is None:
            return None

        if isinstance(self.with_param, Parameter):
            return self.with_param.value
        elif isinstance(self.with_param, str):
            return self.with_param
        return serialize(self.with_param)


@dataclass(kw_only=True)
class WithItemsMixin(BaseMixin):
    """Add `with_items` capability for inheritors, which supports parallelism over supplied items.

    Notes:
        The items passed in `with_items` must be serializable objects
    """

    with_items: Optional[OneOrMany[Any]] = None

    def _build_with_items(self) -> Optional[List[Item]]:
        """Process the `with_items` field and returns an optional list of corresponding `Item`s.

        Notes:
            Tthese `Item`s contain the serialized version of the supplied items/values.
        """
        if self.with_items is None:
            return None

        if isinstance(self.with_items, list):
            items = []
            for item in self.with_items:
                if isinstance(item, Parameter):
                    items.append(Item(root=item.value))
                elif (
                    isinstance(item, str) or isinstance(item, dict) or isinstance(item, float) or isinstance(item, int)
                ):
                    items.append(Item(root=item))
                elif isinstance(item, Item):
                    items.append(item)
                else:
                    items.append(Item(root=serialize(item)))
            return items
        elif isinstance(self.with_items, Parameter):
            return [Item(root=self.with_items.value)]
        elif isinstance(self.with_items, str):
            return [Item(root=self.with_items)]
        return [Item(root=serialize(self.with_items))]


@dataclass(kw_only=True)
class EnvIOMixin(EnvMixin, IOMixin):
    """`EnvIOMixin` provides the capacity to create environment variables from inputs."""

    def _build_params_from_env(self) -> Optional[List[ModelParameter]]:
        """Assemble a list of any environment variables that are set to obtain values from `Parameter`s."""
        if self.env is None:
            return None

        params: Optional[List[ModelParameter]] = None
        for spec in normalize_to_list(self.env):
            if isinstance(spec, Env) and spec.value_from_input is not None:
                value = (
                    spec.value_from_input.value
                    if isinstance(spec.value_from_input, Parameter)
                    else spec.value_from_input
                )
                params = (
                    [ModelParameter(name=spec.param_name, value=value)]
                    if params is None
                    else params + [ModelParameter(name=spec.param_name, value=value)]
                )

        return params or None

    def _build_inputs(self) -> Optional[ModelInputs]:
        """Builds the inputs from the combination of env variables that require specific input parameters to be set."""
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


@dataclass(kw_only=True)
class TemplateInvocatorSubNodeMixin(SubNodeMixin):
    """Used for classes that form sub nodes of Template invocators - `Steps` and `DAG`.

    See Also:
    --------
    https://argoproj.github.io/argo-workflows/workflow-concepts/#template-invocators for more on template invocators.
    """

    name: str
    continue_on: Optional[ContinueOn] = None
    hooks: Optional[Dict[str, LifecycleHook]] = None
    on_exit: Optional[Union[str, Templatable]] = None
    template: Optional[Union[str, Template, Templatable]] = None
    template_ref: Optional[TemplateRef] = None
    inline: Optional[Union[Template, Templatable]] = None
    when: Optional[str] = None
    with_sequence: Optional[Sequence] = None

    _build_obj: Optional[HeraBuildObj] = None

    def __post_init__(self) -> None:
        super().__post_init__()

        def only_one(xs: List):
            xs = list(map(bool, xs))
            return xs.count(True) == 1

        if not only_one([self.template, self.template_ref, self.inline]):
            raise ValueError("Exactly one of ['template', 'template_ref', 'inline'] must be present")

    def __getattribute__(self, name: str) -> Any:
        if _context.declaring:
            # Use object's __getattribute__ to avoid infinite recursion
            build_obj = object.__getattribute__(self, "_build_obj")
            assert build_obj  # Assertions to fix type checking

            fields = get_fields(build_obj.output_class)
            annotations = get_field_annotations(build_obj.output_class)
            if name in fields:
                # If the attribute name is in the build_obj's output class fields, then
                # as we are in a declaring context, the access is for a Task/Step output
                subnode_name = object.__getattribute__(self, "name")
                subnode_type = object.__getattribute__(self, "_subtype")

                from hera.workflows.dag import DAG

                # We don't need to keep track of dependencies for Steps
                if _context.pieces and isinstance(_context.pieces[-1], DAG):
                    _context.pieces[-1]._current_task_depends.add(subnode_name)

                if name == "result":
                    result_templated_str = f"{{{{{subnode_type}.{subnode_name}.outputs.result}}}}"
                    return result_templated_str

                param_or_artifact = construct_io_from_annotation(name, annotations[name])
                output_type = "parameters" if isinstance(param_or_artifact, Parameter) else "artifacts"
                return "{{" + f"{subnode_type}.{subnode_name}.outputs.{output_type}.{param_or_artifact.name}" + "}}"

        return super().__getattribute__(name)

    def _build_on_exit(self) -> Optional[str]:
        """Builds the `on_exit` field `str` representation from the set `Templatable` or the specified `str`."""
        if isinstance(self.on_exit, Templatable):
            return self.on_exit._build_template().name  # type: ignore
        return self.on_exit

    @property
    def _subtype(self) -> str:
        """Provides the subtype specification of the inheritor."""
        raise NotImplementedError("Implement me")

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
        """Returns a `Parameter` specification with the given name containing the `results` of `self`."""
        return Parameter(name=name, value=self.result)

    def _get_parameters_as(self, name: str, subtype: str) -> Parameter:
        """Returns a `Parameter` that represents all the outputs of the specified subtype.

        Parameters
        ----------
        name: str
            The name of the parameter to search for.
        subtype: str
            The inheritor subtype field, used to construct the output artifact `from_` reference.

        Returns:
        -------
        Parameter
            The parameter, named based on the given `name`, along with a value that references all outputs.
        """
        return Parameter(name=name, value=f"{{{{{subtype}.{self.name}.outputs.parameters}}}}")

    def _get_parameter(self, name: str, subtype: str) -> Parameter:
        """Attempts to find the specified parameter in the outputs for the specified subtype.

        Notes:
        -----
        This is specifically designed to be invoked by inheritors.

        Parameters
        ----------
        name: str
            The name of the parameter to search for.
        subtype: str
            The inheritor subtype field, used to construct the output artifact `from_` reference.

        Returns:
        -------
        Parameter
            The parameter if found.

        Raises:
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
        elif isinstance(self.template, Template):
            template = self.template
        else:
            raise ValueError("Only 'template' is supported (not inline or template_ref)")

        if template.outputs is None:
            raise ValueError(f"Cannot get output parameters. Template '{template.name}' has no outputs")
        if template.outputs.parameters is None:
            raise ValueError(f"Cannot get output parameters. Template '{template.name}' has no output parameters")

        parameters = template.outputs.parameters

        obj = next((output for output in parameters if output.name == name), None)
        if obj is not None:
            return Parameter(
                name=obj.name,
                value=f"{{{{{subtype}.{self.name}.outputs.parameters.{name}}}}}",
            )
        raise KeyError(f"No output parameter named `{name}` found")

    def _get_artifact(self, name: str, subtype: str) -> Artifact:
        """Attempts to find the specified artifact in the outputs for the specified subtype.

        Notes:
        -----
        This is specifically designed to be invoked by inheritors.

        Parameters
        ----------
        name: str
            The name of the artifact to search for.
        subtype: str
            The inheritor subtype field, used to construct the output artifact `from_` reference.

        Returns:
        -------
        Artifact
            The artifact if found.

        Raises:
        ------
        ValueError
            When no outputs can be constructed/no outputs are set.
        KeyError
            When the artifact is not found.
        NotImplementedError
            When something else other than an `Artifact` is found for the specified name.
        """
        if isinstance(self.template, str):
            raise ValueError(f"Cannot get output artifacts when the template was set via a name: {self.template}")

        # here, we build the template early to verify that we can get the outputs
        if isinstance(self.template, Templatable):
            template = self.template._build_template()
        elif isinstance(self.template, Template):
            template = self.template
        else:
            raise ValueError("Only 'template' is supported (not inline or template_ref)")

        if template.outputs is None:
            raise ValueError(f"Cannot get output artifacts. Template '{template.name}' has no outputs")
        if template.outputs.artifacts is None:
            raise ValueError(f"Cannot get output artifacts. Template '{template.name}' has no output artifacts")

        artifacts = cast(List[ModelArtifact], template.outputs.artifacts)

        obj = next((output for output in artifacts if output.name == name), None)
        if obj is not None:
            return Artifact(name=name, from_=f"{{{{{subtype}.{self.name}.outputs.artifacts.{name}}}}}")
        raise KeyError(f"No output artifact named `{name}` found")

    def get_parameters_as(self, name: str) -> Parameter:
        """Returns a `Parameter` that represents all the outputs of this subnode.

        Parameters
        ----------
        name: str
            The name of the parameter to search for.

        Returns:
        -------
        Parameter
            The parameter, named based on the given `name`, along with a value that references all outputs.
        """
        return self._get_parameters_as(name=name, subtype=self._subtype)

    def get_artifact(self, name: str) -> Artifact:
        """Gets an artifact from the outputs of this subnode."""
        return self._get_artifact(name=name, subtype=self._subtype)

    def get_parameter(self, name: str) -> Parameter:
        """Gets a parameter from the outputs of this subnode."""
        return self._get_parameter(name=name, subtype=self._subtype)

    def get_outputs_as_arguments(self) -> List[Union[Parameter, Artifact]]:
        """Get all output parameters and artifacts as a combined list from this task/step for use as arguments.

        This is useful for when all the inputs of another template match all the outputs of this template. It
        is also possible to combine the outputs of multiple templates if they collectively match the inputs of
        another template.
        """
        if isinstance(self.template, str):
            raise ValueError(f"Cannot get outputs when the template was set via a name: {self.template}")

        # here, we build the template early to verify that we can get the outputs
        if isinstance(self.template, Templatable):
            template = self.template._build_template()
        elif isinstance(self.template, Template):
            template = self.template
        else:
            raise ValueError("Only 'template' is supported (not inline or template_ref)")

        if template.outputs is None:
            raise ValueError(f"Template '{template.name}' has no outputs")

        parameters = [self.get_parameter(p.name) for p in template.outputs.parameters or []]
        artifacts = [self.get_artifact(art.name) for art in template.outputs.artifacts or []]

        result = parameters + artifacts
        if not result:
            raise ValueError(f"Template '{template.name}' has no outputs")

        return result
