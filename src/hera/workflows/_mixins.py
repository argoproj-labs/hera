"""Core collection of Hera mixins that isolate shareable functionality between Hera objects."""
from __future__ import annotations

import functools
import inspect
from pathlib import Path

try:
    from inspect import get_annotations  # type: ignore
except ImportError:
    from hera.workflows._inspect import get_annotations  # type: ignore
from collections import ChainMap
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set, Type, TypeVar, Union, cast

try:
    from typing import Annotated, get_args, get_origin  # type: ignore
except ImportError:
    from typing_extensions import Annotated, get_args, get_origin  # type: ignore

from pydantic import root_validator, validator

from hera.shared import BaseMixin, global_config
from hera.shared._base_model import BaseModel
from hera.shared.serialization import serialize
from hera.workflows._context import SubNodeMixin, _context
from hera.workflows.artifact import Artifact
from hera.workflows.env import Env, _BaseEnv
from hera.workflows.env_from import _BaseEnvFrom
from hera.workflows.exceptions import InvalidTemplateCall
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
from hera.workflows.parameter import Parameter
from hera.workflows.protocol import Templatable, TWorkflow
from hera.workflows.resources import Resources
from hera.workflows.user_container import UserContainer
from hera.workflows.volume import Volume, _BaseVolume

if TYPE_CHECKING:
    from hera.workflows.steps import Step
    from hera.workflows.task import Task

_yaml: Optional[ModuleType] = None
try:
    import yaml

    _yaml = yaml
except ImportError:
    _yaml = None

InputsT = Optional[
    Union[
        ModelInputs,
        Union[Parameter, ModelParameter, Artifact, ModelArtifact, Dict[str, Any]],
        List[Union[Parameter, ModelParameter, Artifact, ModelArtifact, Dict[str, Any]]],
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
        Union[Parameter, ModelParameter, Artifact, ModelArtifact],
        List[Union[Parameter, ModelParameter, Artifact, ModelArtifact]],
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
        Union[Parameter, ModelParameter, Artifact, ModelArtifact, Dict[str, Any]],
        List[Union[Parameter, ModelParameter, Artifact, ModelArtifact, Dict[str, Any]]],
    ]
]
"""`ArgumentsT` is the main type associated with arguments that can be used on DAG tasks, steps, etc.

This type enables uses of the Hera auto-generated `hera.workflows.models.Arguments` model, Hera managed models such as 
`hera.workflows.Parameter`, `hera.workflows.Artifact`, a dictionary mapping of parameter names to values, or a list of
any of the aforementioned objects.
"""

MetricsT = Optional[
    Union[
        _BaseMetric,
        List[_BaseMetric],
        Metrics,
        ModelPrometheus,
        List[ModelPrometheus],
        ModelMetrics,
    ]
]
"""`MetricsT` is the core Hera type for Prometheus metrics. 

This metrics type enables users to use either auto-generated Hera metrics, lists of auto-generated single metrics, or
the variations of metrics provided by `hera.workflows.metrics.*`  
"""

EnvT = Optional[
    Union[
        _BaseEnv,
        EnvVar,
        List[Union[_BaseEnv, EnvVar, Dict[str, Any]]],
        Dict[str, Any],
    ]
]
"""`EnvT` is the core Hera type for environment variables.

The env type enables setting single valued environment variables, lists of environment variables, or dictionary 
mappings of env variables names to values, which are automatically parsed by Hera.
"""

EnvFromT = Optional[Union[_BaseEnvFrom, EnvFromSource, List[Union[_BaseEnvFrom, EnvFromSource]]]]
"""`EnvFromT` is the core Hera type for environment variables derived from Argo/Kubernetes sources.

This env type enables specifying environment variables in base form, as `hera.workflows.env` form, or lists of the 
aforementioned objects.
"""

VolumesT = Optional[Union[Union[ModelVolume, _BaseVolume], List[Union[ModelVolume, _BaseVolume]]]]
"""`VolumesT` is the core Hera type for volumes. 

This volume type is used to specify the configuration of volumes to be automatically created by Argo/K8s and mounted
by Hera at specific mount paths in containers.
"""

TContext = TypeVar("TContext", bound="ContextMixin")
"""`TContext` is the bounded context controlled by the context mixin that enable context management in workflow/dag"""

THookable = TypeVar("THookable", bound="HookMixin")
"""`THookable` is the type associated with mixins that provide the ability to apply hooks from the global config"""


class HookMixin(BaseMixin):
    """`HookMixin` provides the ability to dispatch hooks set on the global config to any inheritors."""

    def _dispatch_hooks(self: THookable) -> THookable:
        """Dispatches the global hooks on the current object."""
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
    """`ContextMixin` provides the ability to implement context management.

    The mixin implements the `__enter__` and `__exit__` functionality that enables the core `with` clause. The mixin
    expects that inheritors implement the `_add_sub` functionality, which adds a node defined within the context to the
    main object context such as `Workflow`, `DAG`, or `ContainerSet`.
    """

    def __enter__(self: TContext) -> TContext:
        """Enter the context of the inheritor."""
        _context.enter(self)
        return self

    def __exit__(self, *_) -> None:
        """Leave the context of the inheritor."""
        _context.exit()

    def _add_sub(self, node: Any) -> Any:
        """Adds the supplied node to the context of the inheritor."""
        raise NotImplementedError()


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
    termination_message_policy: Optional[TerminationMessagePolicy] = None
    tty: Optional[bool] = None

    def _build_image_pull_policy(self) -> Optional[ImagePullPolicy]:
        """Processes the image pull policy field and returns a generated `ImagePullPolicy` enum."""
        if self.image_pull_policy is None:
            return None
        elif isinstance(self.image_pull_policy, ImagePullPolicy):
            return self.image_pull_policy

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
            return ImagePullPolicy[policy_mapper[self.image_pull_policy].name]
        except KeyError as e:
            raise KeyError(
                f"Supplied image policy {self.image_pull_policy} is not valid. "
                "Use one of {ImagePullPolicy.__members__}"
            ) from e

    @validator("image", pre=True, always=True)
    def _set_image(cls, v):
        """Validator that sets the image field to the global image unless the image is specified on the container."""
        if v is None:
            return global_config.image
        return v


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

    def _build_inputs(self) -> Optional[ModelInputs]:
        """Processes the `inputs` field and returns a generated `ModelInputs`."""
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

        # returning `None` for `ModelInputs` means the submission to the server will not even have the `outputs` field
        # set, which saves some space
        if result.parameters is None and result.artifacts is None:
            return None
        return result


class EnvMixin(BaseMixin):
    """`EnvMixin` provides the ability to set simple env variables along with env variables that are derived."""

    env: EnvT = None
    env_from: EnvFromT = None

    def _build_env(self) -> Optional[List[EnvVar]]:
        """Processes the `env` field and returns a list of generated `EnvVar` or `None`."""
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

        # returning `None` for `envs` means the submission to the server will not even have the `envs` field
        # set, which saves some space
        return result if result else None

    def _build_env_from(self) -> Optional[List[EnvFromSource]]:
        """Processes the `env_from` field and returns a list of generated `EnvFrom` or `None`."""
        if self.env_from is None:
            return None

        result: List[EnvFromSource] = []
        env_from = self.env_from if isinstance(self.env_from, list) else [self.env_from]
        for e in env_from:
            if isinstance(e, EnvFromSource):
                result.append(e)
            elif issubclass(e.__class__, _BaseEnvFrom):
                result.append(e.build())

        # returning `None` for `envs` means the submission to the server will not even have the `env_from` field
        # set, which saves some space
        return result if result else None


class MetricsMixin(BaseMixin):
    """`MetricsMixin` provides the ability to set metrics on a n object."""

    metrics: MetricsT = None

    def _build_metrics(self) -> Optional[ModelMetrics]:
        """Processes the `metrics` field and returns the generated `ModelMetrics` or `None`."""
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
        return ModelMetrics(prometheus=metrics) if metrics else None


class TemplateMixin(SubNodeMixin, HookMixin, MetricsMixin):
    """`TemplateMixin` provides the Argo template fields that are shared between different sub-template fields.

    The supported sub-template fields are `Script`, `Data`, `DAG`, `Resource`, `Container`, `ContainerSet`, etc.
    """

    active_deadline_seconds: Optional[
        Union[int, str, IntOrString]
    ] = None  # TODO: This type blocks YAML roundtrip. Consider using type: Optional[int]
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

    def _build_sidecars(self) -> Optional[List[ModelUserContainer]]:
        """Builds the `sidecars` field and optionally returns a list of `UserContainer`."""
        if self.sidecars is None:
            return None

        if isinstance(self.sidecars, UserContainer):
            return [self.sidecars.build()]

        return [s.build() for s in self.sidecars]

    def _build_active_deadline_seconds(self) -> Optional[IntOrString]:
        """Builds the `active_deadline_seconds` field and optionally returns a generated `IntOrString`."""
        if self.active_deadline_seconds is None:
            return None

        return IntOrString(__root__=str(self.active_deadline_seconds))

    def _build_metadata(self) -> Optional[Metadata]:
        """Builds the `metadata` field of the template since the `annotations` and `labels` fields are separated."""
        if self.annotations is None and self.labels is None:
            return None

        return Metadata(
            annotations=self.annotations,
            labels=self.labels,
        )


class ResourceMixin(BaseMixin):
    """`ResourceMixin` provides the capability to set resources such as compute requirements like CPU, GPU, etc."""

    resources: Optional[Union[ResourceRequirements, Resources]] = None

    def _build_resources(self) -> Optional[ResourceRequirements]:
        """Parses the resources and returns a generated `ResourceRequirements` object."""
        if self.resources is None or isinstance(self.resources, ResourceRequirements):
            return self.resources
        return self.resources.build()


class VolumeMixin(BaseMixin):
    """`VolumeMixin` provides the ability to set volumes on an inheriting resource.

    Note that *any* volumes set on the `volumes` field automatically get an associated persistent volume claim
    constructed and set on the workflow. This way users do not have to set the PVC themselves. However, clients of the
    mixin should be careful to *not* generate multiple PVCs for the same volume.
    """

    volumes: VolumesT = None

    def _build_volumes(self) -> Optional[List[ModelVolume]]:
        """Processes the `volumes` and creates an optional list of generates `Volume`s."""
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
        """Generates the list of persistent volume claims to associate with the set `volumes`."""
        if self.volumes is None:
            return None

        volumes = self.volumes if isinstance(self.volumes, list) else [self.volumes]
        volumes_with_pv_claims = [v for v in volumes if isinstance(v, Volume)]
        if not volumes_with_pv_claims:
            return None
        return [v._build_persistent_volume_claim() for v in volumes_with_pv_claims] or None


class VolumeMountMixin(VolumeMixin):
    """`VolumeMountMixin` supports setting `volume_devices` and `volume_mounts` on the inheritor.

    Devices and mounts are approaches for mounting existing volume resources from a cluster on the job that is
    created via inheriting from this mixin.
    """

    volume_devices: Optional[List[VolumeDevice]] = None
    volume_mounts: Optional[List[VolumeMount]] = None

    def _build_volume_mounts(self) -> Optional[List[VolumeMount]]:
        """Processes the `volume_mounts` field and generates an optional list of `VolumeMount`s."""
        # while it's possible for `volume_mounts` to be `None`, this has to check that `volumes` is also `None` since
        # it's possible that Hera can find volume mounts to generate for the user if there are any volumes set
        if self.volume_mounts is None and self.volumes is None:
            return None

        if self.volumes is None:
            volumes = []
        else:
            volumes = self.volumes if isinstance(self.volumes, list) else [self.volumes]

        result = (
            None
            if not volumes
            else [v._build_volume_mount() if issubclass(v.__class__, _BaseVolume) else v for v in volumes]
        )

        if result is None and self.volume_mounts is None:
            return None
        elif result is None and self.volume_mounts is not None:
            return self.volume_mounts
        elif result is not None and self.volume_mounts is None:
            return cast(List[VolumeMount], result)

        return cast(List[VolumeMount], self.volume_mounts) + cast(List[VolumeMount], result)


class ArgumentsMixin(BaseMixin):
    """`ArgumentsMixin` provides the ability to set the `arguments` field on the inheriting object."""

    arguments: ArgumentsT = None

    def _build_arguments(self) -> Optional[ModelArguments]:
        """Processes the `arguments` field and builds the optional generated `Arguments` to set as arguments."""
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
                    result.parameters = (
                        [value.as_argument()]
                        if result.parameters is None
                        else result.parameters + [value.as_argument()]
                    )
            elif isinstance(arg, ModelArtifact):
                result.artifacts = [arg] if result.artifacts is None else result.artifacts + [arg]
            elif isinstance(arg, Artifact):
                result.artifacts = (
                    [arg._build_artifact()] if result.artifacts is None else result.artifacts + [arg._build_artifact()]
                )
            elif isinstance(arg, Parameter):
                result.parameters = (
                    [arg.as_argument()] if result.parameters is None else result.parameters + [arg.as_argument()]
                )
            elif isinstance(arg, ModelParameter):
                result.parameters = [arg] if result.parameters is None else result.parameters + [arg]
        # returning `None` for `Arguments` means the submission to the server will not even have the
        # `arguments` field set, which saves some payload
        if result.parameters is None and result.artifacts is None:
            return None
        return result


class CallableTemplateMixin(ArgumentsMixin):
    """`CallableTemplateMixin` provides the ability to 'call' the template like a regular Python function.

    The callable template implements the `__call__` method for the inheritor. The `__call__` method supports invoking
    the template as a regular Python function. The call must be executed within an active context, which is a
    `Workflow`, `DAG` or `Steps` context since the call optionally returns a `Step` or a `Task` depending on the active
    context (`None` for `Workflow`, `Step` for `Steps` and `Task` for `DAG`). Note that `Steps` also supports calling
    templates in a parallel steps context via using `Steps(...).parallel()`. When the call is executed and the template
    does not exist on the active context, i.e. the workflow, it is automatically added for the user. Note that invoking
    the same template multiple times does *not* result in the creation/addition of the same template to the active
    context/workflow. Rather, a union is performed, so space is saved for users on the templates field and templates are
    not duplicated.
    """

    def __call__(self, *args, **kwargs) -> Union[None, Step, Task]:
        if "name" not in kwargs:
            kwargs["name"] = self.name  # type: ignore

        arguments = self._get_arguments(**kwargs)
        parameter_names = self._get_parameter_names(arguments)
        artifact_names = self._get_artifact_names(arguments)

        # when the `source` is set via an `@script` decorator, it does not come in with the `kwargs` so we need to
        # set it here in order for the following logic to capture it
        if "source" not in kwargs and hasattr(self, "source"):
            kwargs["source"] = self.source  # type: ignore

        if "source" in kwargs and "with_param" in kwargs:
            arguments += self._get_deduped_params_from_source(parameter_names, artifact_names, kwargs["source"])
        elif "source" in kwargs and "with_items" in kwargs:
            arguments += self._get_deduped_params_from_items(parameter_names, kwargs["with_items"])

        # it is possible for the user to pass `arguments` via `kwargs` along with `with_param`. The `with_param`
        # additional parameters are inferred and have to be added to the `kwargs['arguments']`, otherwise
        # the step/task will miss adding them when building the final arguments
        kwargs["arguments"] = arguments

        from hera.workflows.dag import DAG
        from hera.workflows.script import Script
        from hera.workflows.steps import Parallel, Step, Steps
        from hera.workflows.task import Task
        from hera.workflows.workflow import Workflow

        if _context.pieces:
            if isinstance(_context.pieces[-1], Workflow):
                # Notes on callable templates under a Workflow:
                # * If the user calls a script directly under a Workflow (outside of a Steps/DAG) then we add the script
                #   template to the workflow and return None.
                # * Containers, ContainerSets and Data objects (i.e. subclasses of CallableTemplateMixin) are already
                #   added when initialized under the Workflow context so a callable doesn't make sense in that context,
                #   so we raise an InvalidTemplateCall exception.
                # * We do not currently validate the added templates to stop a user adding the same template multiple
                #   times, which can happen if "calling" the same script multiple times to add it to the workflow,
                #   or initializing a second `Container` exactly like the first.
                if isinstance(self, Script):
                    _context.add_sub_node(self)
                    return None

                raise InvalidTemplateCall(
                    f"Callable Template '{self.name}' is not callable under a Workflow"  # type: ignore
                )
            if isinstance(_context.pieces[-1], (Steps, Parallel)):
                return Step(*args, template=self, **kwargs)

            if isinstance(_context.pieces[-1], DAG):
                return Task(*args, template=self, **kwargs)

        raise InvalidTemplateCall(
            f"Callable Template '{self.name}' is not under a Workflow, Steps, Parallel, or DAG context"  # type: ignore
        )

    def _get_arguments(self, **kwargs) -> List:
        """Returns a list of arguments from the kwargs given to the template call."""
        # these are the already set parameters. If a user has already set a parameter argument, then Hera
        # uses the user-provided value rather than the inferred value
        kwargs_arguments = kwargs.get("arguments", [])
        kwargs_arguments = kwargs_arguments if isinstance(kwargs_arguments, List) else [kwargs_arguments]  # type: ignore
        arguments = self.arguments if isinstance(self.arguments, List) else [self.arguments] + kwargs_arguments  # type: ignore
        return list(filter(lambda x: x is not None, arguments))

    def _get_parameter_names(self, arguments: List) -> Set[str]:
        """Returns the union of parameter names from the given arguments' parameter objects and dictionary keys."""
        parameters = [arg for arg in arguments if isinstance(arg, (ModelParameter, Parameter))]
        keys = [arg for arg in arguments if isinstance(arg, dict)]
        return {p.name for p in parameters}.union(
            set(functools.reduce(lambda x, y: cast(List[str], x) + list(y.keys()), keys, []))
        )

    def _get_artifact_names(self, arguments: List) -> Set[str]:
        """Returns the set of artifact names that are currently set on the mixin inheritor."""
        artifacts = [arg for arg in arguments if isinstance(arg, (ModelArtifact, Artifact))]
        return {a if isinstance(a, str) else a.name for a in artifacts if a.name}

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

        Returns:
        -------
        List[Parameter]
            The list of inferred arguments to set.
        """
        new_arguments = []
        new_parameters = _get_param_items_from_source(source)
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

        Returns:
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


class ItemMixin(BaseMixin):
    """Add `with_items` capability for inheritors, which supports parallelism over supplied items.

    Notes:
        The items passed in `with_items` must be serializable objects
    """

    with_items: Optional[List[Any]] = None

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
    """`EnvIOMixin` provides the capacity to use environment variables."""

    def _build_params_from_env(self) -> Optional[List[Parameter]]:
        """Assemble a list of any environment variables that are set to obtain values from `Parameter`s."""
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


class TemplateInvocatorSubNodeMixin(BaseMixin):
    """Used for classes that form sub nodes of Template invocators - `Steps` and `DAG`.

    See Also:
    --------
    https://argoproj.github.io/argo-workflows/workflow-concepts/#template-invocators for more on template invocators.
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

    @root_validator(pre=False)
    def _check_values(cls, values):
        """Validates that a single field is set between `template`, `template_ref`, and `inline`."""

        def one(xs: List):
            xs = list(map(bool, xs))
            return xs.count(True) == 1

        if not one([values.get("template"), values.get("template_ref"), values.get("inline")]):
            raise ValueError("Exactly one of ['template', 'template_ref', 'inline'] must be present")
        return values

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


def _get_param_items_from_source(source: Callable) -> List[Parameter]:
    """Returns a list (possibly empty) of `Parameter` from the specified `source`.

    This infers that each non-keyword, positional, argument of the given source is a parameter that stems from a
    fanout. Therefore, each parameter value takes the form of `{{item}}` when there's a single argument or
    `{{item.<argument name>}}` when there are other arguments.

    Returns:
    -------
    List[Parameter]
        A list of identified parameters (possibly empty).
    """
    source_signature: List[str] = []
    for p in inspect.signature(source).parameters.values():
        if p.default == inspect.Parameter.empty and p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            # only add positional or keyword arguments that are not set to a default value
            # as the default value ones are captured by the automatically generated `Parameter` fields for positional
            # kwargs. Otherwise, we assume that the user sets the value of the parameter via the `with_param` field
            source_signature.append(p.name)

    if len(source_signature) == 1:
        return [Parameter(name=n, value="{{item}}") for n in source_signature]
    return [Parameter(name=n, value=f"{{{{item.{n}}}}}") for n in source_signature]


def _get_params_from_items(with_items: List[Any]) -> Optional[List[Parameter]]:
    """Returns an optional list of `Parameter` from the specified list of `with_items`.

    The assembled list of `Parameter` contains all the unique parameters identified from the `with_items` list. For
    example, if the `with_items` list contains 3 serializable elements such as
    `[{'a': 1, 'b': 2}, {'a': 3, 'b': 4}, {'a': 5, 'b': 6}]`, then only 2 `Parameter`s are returned. Namely, only
     `Parameter(name='a')` and `Parameter(name='b')` is returned, with values `{{item.a}}` and `{{item.b}}`,
     respectively. This helps with the parallel/serial processing of the supplied items.
    """
    if len(with_items) == 0:
        return None
    elif len(with_items) == 1:
        el = with_items[0]
        if len(el.keys()) == 1:
            return [Parameter(name=n, value="{{item}}") for n in el.keys()]
        else:
            return [Parameter(name=n, value=f"{{{{item.{n}}}}}") for n in el.keys()]
    return [Parameter(name=n, value=f"{{{{item.{n}}}}}") for n in with_items[0].keys()]


def _set_model_attr(model: BaseModel, attrs: List[str], value: Any):
    # The `attrs` list represents a path to an attribute in `model`, whose attributes
    # are BaseModels themselves. Therefore we use `getattr` to get a reference to the final
    # BaseModel set to `curr`, then call `setattr` on that BaseModel, using the last attribute
    # name in attrs, and the value passed in.
    curr: BaseModel = model
    for attr in attrs[:-1]:
        curr = getattr(curr, attr)

    setattr(curr, attrs[-1], value)


def _get_model_attr(model: BaseModel, attrs: List[str]) -> Any:
    # This is almost the same as _set_model_attr.
    # The `attrs` list represents a path to an attribute in `model`, whose attributes
    # are BaseModels themselves. Therefore we use `getattr` to get a reference to the final
    # BaseModel set to `curr`, then `getattr` on that BaseModel, using the last attribute
    # name in attrs.
    curr: BaseModel = model
    for attr in attrs[:-1]:
        curr = getattr(curr, attr)

    return getattr(curr, attrs[-1])


class ModelMapperMixin(BaseMixin):
    class ModelMapper:
        def __init__(self, model_path: str, hera_builder: Optional[Callable] = None):
            self.model_path = None
            self.builder = hera_builder

            if not model_path:
                # Allows overriding parent attribute annotations to remove the mapping
                return

            self.model_path = model_path.split(".")
            curr_class: Type[BaseModel] = self._get_model_class()
            for key in self.model_path:
                if key not in curr_class.__fields__:
                    raise ValueError(f"Model key '{key}' does not exist in class {curr_class}")
                curr_class = curr_class.__fields__[key].outer_type_

        @classmethod
        def _get_model_class(cls) -> Type[BaseModel]:
            raise NotImplementedError

        @classmethod
        def build_model(
            cls, hera_class: Type[ModelMapperMixin], hera_obj: ModelMapperMixin, model: TWorkflow
        ) -> TWorkflow:
            assert isinstance(hera_obj, ModelMapperMixin)

            for attr, annotation in hera_class._get_all_annotations().items():
                if get_origin(annotation) is Annotated and isinstance(
                    get_args(annotation)[1], ModelMapperMixin.ModelMapper
                ):
                    mapper = get_args(annotation)[1]
                    # Value comes from builder function if it exists on hera_obj, otherwise directly from the attr
                    value = (
                        getattr(hera_obj, mapper.builder.__name__)()
                        if mapper.builder is not None
                        else getattr(hera_obj, attr)
                    )
                    if value is not None:
                        _set_model_attr(model, mapper.model_path, value)

            return model

    @classmethod
    def _get_all_annotations(cls) -> ChainMap:
        """Gets all annotations of this class and any parent classes."""
        return ChainMap(*(get_annotations(c) for c in cls.__mro__))

    @classmethod
    def _from_model(cls, model: BaseModel) -> ModelMapperMixin:
        """Parse from given model to cls's type."""
        hera_obj = cls()

        for attr, annotation in cls._get_all_annotations().items():
            if get_origin(annotation) is Annotated and isinstance(
                get_args(annotation)[1], ModelMapperMixin.ModelMapper
            ):
                mapper = get_args(annotation)[1]
                if mapper.model_path:
                    value = _get_model_attr(model, mapper.model_path)
                    if value is not None:
                        setattr(hera_obj, attr, value)

        return hera_obj

    @classmethod
    def _from_dict(cls, model_dict: Dict, model: Type[BaseModel]) -> ModelMapperMixin:
        """Parse from given model_dict, using the given model type to call its parse_obj."""
        model_workflow = model.parse_obj(model_dict)
        return cls._from_model(model_workflow)

    @classmethod
    def from_dict(cls, model_dict: Dict) -> ModelMapperMixin:
        """Parse from given model_dict."""
        raise NotImplementedError

    @classmethod
    def _from_yaml(cls, yaml_str: str, model: Type[BaseModel]) -> ModelMapperMixin:
        """Parse from given yaml string, using the given model type to call its parse_obj."""
        if not _yaml:
            raise ImportError("PyYAML is not installed")
        return cls._from_dict(_yaml.safe_load(yaml_str), model)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> ModelMapperMixin:
        """Parse from given yaml_str."""
        raise NotImplementedError

    @classmethod
    def _from_file(cls, yaml_file: Union[Path, str], model: Type[BaseModel]) -> ModelMapperMixin:
        yaml_file = Path(yaml_file)
        return cls._from_yaml(yaml_file.read_text(encoding="utf-8"), model)

    @classmethod
    def from_file(cls, yaml_file: Union[Path, str]) -> ModelMapperMixin:
        """Parse from given yaml_file."""
        raise NotImplementedError


class ExperimentalMixin(BaseMixin):
    _experimental_warning_message: str = (
        "Unable to instantiate {} since it is an experimental feature."
        " Please turn on experimental features by setting "
        '`hera.shared.global_config.experimental_features["{}"] = True`.'
        " Note that experimental features are unstable and subject to breaking changes."
    )

    _flag: str

    @root_validator
    def _check_enabled(cls, values):
        if not global_config.experimental_features[cls._flag]:
            raise ValueError(cls._experimental_warning_message.format(cls, cls._flag))
        return values
