from __future__ import annotations

from typing import Dict, List, Optional, TypeVar, Union, cast

from hera.shared.global_config import GlobalConfig
from hera.workflows._base_model import BaseModel as _BaseModel
from hera.workflows.models import (
    HTTP,
    Affinity,
    Arguments,
    Artifact,
    ArtifactLocation,
    ContainerPort,
    ContinueOn,
)
from hera.workflows.models import DAGTask as _ModelDAGTask
from hera.workflows.models import (
    EnvFromSource,
    EnvVar,
    ExecutorConfig,
    HostAlias,
    ImagePullPolicy,
)
from hera.workflows.models import Inputs as ModelInputs
from hera.workflows.models import (
    IntOrString,
    Item,
    LifecycleHook,
    Memoize,
    Metadata,
    Metrics,
)
from hera.workflows.models import Outputs as ModelOutputs
from hera.workflows.models import Parameter as ModelParameter
from hera.workflows.models import (
    Plugin,
    PodSecurityContext,
    Probe,
    ResourceRequirements,
    RetryStrategy,
    Sequence,
    Synchronization,
    Template,
    TemplateRef,
    TerminationMessagePolicy,
    Toleration,
)
from hera.workflows.models import UserContainer as ModelUserContainer
from hera.workflows.models import Volume, VolumeDevice, VolumeMount
from hera.workflows.v5.env import _BaseEnv
from hera.workflows.v5.env_from import _BaseEnvFrom
from hera.workflows.v5.operator import Operator
from hera.workflows.v5.parameter import Parameter
from hera.workflows.v5.resources import Resources
from hera.workflows.v5.task_result import TaskResult
from hera.workflows.v5.user_container import UserContainer
from hera.workflows.v5.volume import _BaseVolume
from hera.workflows.v5.workflow_status import WorkflowStatus

Inputs = List[Union[ModelInputs, Parameter, ModelParameter, Artifact]]
Outputs = List[Union[ModelOutputs, Parameter, ModelParameter, Artifact]]
TSub = TypeVar("TSub", bound="_SubNodeMixin")


class _BaseMixin(_BaseModel):
    pass


class _SubNodeMixin(_BaseModel):
    """_SubMixin ensures that the class gets added to the Hera context on initialization."""

    def __post_init__(self: TSub) -> TSub:
        from hera.workflows.v5._context import _context

        _context.add_sub_node(self)
        return self


class _ContainerMixin(_BaseMixin):
    image: str = GlobalConfig.image
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
        if self.image_pull_policy is None or isinstance(self.image_pull_policy, ImagePullPolicy):
            return self.image_pull_policy
        return ImagePullPolicy[self.image_pull_policy.lower()]


class _IOMixin(_BaseMixin):
    inputs: Optional[Inputs] = None
    outputs: Optional[Outputs] = None

    def _build_inputs(self) -> Optional[ModelInputs]:
        if self.inputs is None:
            return None
        elif isinstance(self.inputs, ModelInputs):
            return self.inputs

        result = ModelInputs()
        for value in self.inputs:
            if isinstance(value, Parameter):
                result.parameters = (
                    [value.as_input()] if result.parameters is None else result.parameters + [value.as_input()]
                )
            elif isinstance(value, ModelParameter):
                result.parameters = [value] if result.parameters is None else result.parameters + [value]
            elif isinstance(value, Artifact):
                result.artifacts = [value] if result.artifacts is None else result.artifacts + [value]

        if result.parameters is None and result.artifacts is None:
            return None
        return result

    def _build_outputs(self) -> Optional[ModelOutputs]:
        if self.outputs is None:
            return None
        elif isinstance(self.outputs, ModelOutputs):
            return self.outputs

        result = ModelOutputs()
        for value in self.outputs:
            if isinstance(value, Parameter):
                result.parameters = (
                    [value.as_output()] if result.parameters is None else result.parameters + [value.as_output()]
                )
            elif isinstance(value, ModelParameter):
                result.parameters = [value] if result.parameters is None else result.parameters + [value]
            elif isinstance(value, Artifact):
                result.artifacts = [value] if result.artifacts is None else result.artifacts + [value]

        if result.parameters is None and result.artifacts is None:
            return None
        return result


class _EnvMixin(_BaseMixin):
    env: Optional[List[Union[_BaseEnv, EnvVar]]] = None
    env_from: Optional[List[Union[_BaseEnvFrom, EnvFromSource]]] = None

    def _build_env(self) -> Optional[EnvVar]:
        if self.env is None or isinstance(self.env, EnvVar):
            return self.env

        v = cast(_BaseEnv, self.env)
        return v.build()

    def _build_env_from(self) -> Optional[EnvFromSource]:
        if self.env_from is None or isinstance(self.env_from, EnvFromSource):
            return self.env_from

        v = cast(_BaseEnvFrom, self.env_from)
        return v.build()


class _TemplateMixin(_BaseMixin):
    name: str
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
    metrics: Optional[Metrics] = None
    node_selector: Optional[Dict[str, str]] = None
    http: Optional[HTTP] = None
    plugin: Optional[Plugin] = None
    pod_spec_patch: Optional[str] = None
    priority: Optional[int] = None
    priority_class_name: Optional[str] = None
    retry_strategy: Optional[RetryStrategy] = None
    scheduler_name: Optional[str] = None
    pod_security_context: Optional[PodSecurityContext] = None
    service_account_name: Optional[str] = None
    sidecars: Optional[List[UserContainer]] = None
    synchronization: Optional[Synchronization] = None
    timeout: Optional[str] = None
    tolerations: Optional[List[Toleration]] = None

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


class _ResourceMixin(_BaseMixin):
    resources: Optional[Union[ResourceRequirements, Resources]] = None

    def _build_resources(self) -> Optional[ResourceRequirements]:
        if self.resources is None or isinstance(self.resources, ResourceRequirements):
            return self.resources

        return self.resources.build()


class _VolumeMountMixin(_BaseMixin):
    volume_devices: Optional[List[VolumeDevice]] = None
    volume_mounts: Optional[List[VolumeMount]] = None
    volumes: Optional[List[_BaseVolume]] = None

    def _build_volume_mounts(self) -> Optional[List[VolumeMount]]:
        if self.volume_mounts is None and self.volumes is None:
            return None

        result = None if self.volumes is None else [v._build_volume_mount() for v in self.volumes]
        if result is None:
            return None

        return cast(List[VolumeMount], self.volume_mounts) + result

    def _build_volumes(self) -> Optional[List[Volume]]:
        if self.volumes is None:
            return None
        return [v._build_volume() for v in self.volumes]


class _DAGTaskMixin(_BaseMixin):
    name: str
    arguments: Optional[Arguments] = None
    continue_on: Optional[ContinueOn] = None
    dependencies: Optional[List[str]] = None
    depends: Optional[str] = None
    hooks: Optional[Dict[str, LifecycleHook]]
    on_exit: Optional[str] = None
    template: Optional[str] = None
    template_ref: Optional[TemplateRef] = None
    inline: Optional[Template] = None
    when: Optional[str] = None
    with_items: Optional[List[Item]] = None
    with_param: Optional[str] = None
    with_sequence: Optional[Sequence] = None

    def _get_dependency_tasks(self) -> List[str]:
        if self.depends is None:
            return []

        # filter out operators
        all_operators = [o for o in Operator]
        tasks = [t for t in self.depends.split() if t not in all_operators]

        # remove dot suffixes
        task_names = [t.split(".")[0] for t in tasks]
        return task_names

    @property
    def id(self) -> str:
        return f"{{{{tasks.{self.name}.id}}}}"

    @property
    def ip(self) -> str:
        return f"{{{{tasks.{self.name}.ip}}}}"

    @property
    def status(self) -> str:
        return f"{{{{tasks.{self.name}.status}}}}"

    @property
    def exit_code(self) -> str:
        return f"{{{{tasks.{self.name}.exitCode}}}}"

    @property
    def started_at(self) -> str:
        return f"{{{{tasks.{self.name}.startedAt}}}}"

    @property
    def finished_at(self) -> str:
        return f"{{{{tasks.{self.name}.finishedAt}}}}"

    @property
    def result(self) -> str:
        return f"{{{{tasks.{self.name}.outputs.result}}}}"

    def next(
        self, other: _DAGTaskMixin, operator: Operator = Operator.and_, on: Optional[TaskResult] = None
    ) -> _DAGTaskMixin:
        assert issubclass(other.__class__, _DAGTaskMixin)

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

    def __rrshift__(self, other: List[_DAGTaskMixin]) -> _DAGTaskMixin:
        assert isinstance(other, list), f"Unknown type {type(other)} specified using reverse right bitshift operator"
        for o in other:
            o.next(self)
        return self

    def __rshift__(
        self, other: Union["_DAGTaskMixin", List["_DAGTaskMixin"]]
    ) -> Union[_DAGTaskMixin, List[_DAGTaskMixin]]:
        if isinstance(other, _DAGTaskMixin):
            return self.next(other)
        elif isinstance(other, list):
            for o in other:
                assert isinstance(
                    o, _DAGTaskMixin
                ), f"Unknown list item type {type(o)} specified using right bitshift operator `>>`"
                self.next(o)
            return other
        raise ValueError(f"Unknown type {type(other)} provided to `__rshift__`")

    def on_workflow_status(self, status: WorkflowStatus, op: Operator = Operator.equals) -> _DAGTaskMixin:
        expression = f"{{{{workflow.status}}}} {op} {status}"
        if self.when:
            self.when += f" {Operator.and_} {expression}"
        else:
            self.when = expression
        return self

    def on_success(self, other: _DAGTaskMixin) -> _DAGTaskMixin:
        return self.next(other, on=TaskResult.succeeded)

    def on_failure(self, other: _DAGTaskMixin) -> _DAGTaskMixin:
        return self.next(other, on=TaskResult.failed)

    def on_error(self, other: _DAGTaskMixin) -> _DAGTaskMixin:
        return self.next(other, on=TaskResult.errored)

    def on_other_result(self, other: _DAGTaskMixin, value: str, operator: Operator = Operator.equals) -> _DAGTaskMixin:
        expression = f"'{other.result}' {operator} {value}"
        if self.when:
            self.when += f" {Operator.and_} {expression}"
        else:
            self.when = expression
        other.next(self)
        return self

    def when_any_succeeded(self, other: _DAGTaskMixin) -> _DAGTaskMixin:
        assert (self.with_param is not None) or (
            self.with_sequence is not None
        ), "Can only use `when_all_failed` when using `with_param` or `with_sequence`"

        return self.next(other, on=TaskResult.any_succeeded)

    def when_all_failed(self, other: _DAGTaskMixin) -> _DAGTaskMixin:
        assert (self.with_param is not None) or (
            self.with_sequence is not None
        ), "Can only use `when_all_failed` when using `with_param` or `with_sequence`"

        return self.next(other, on=TaskResult.all_failed)

    def _build_dag_task(self) -> _ModelDAGTask:
        return _ModelDAGTask(
            arguments=self.arguments,
            continue_on=self.continue_on,
            dependencies=self.dependencies,
            depends=self.depends,
            hooks=self.hooks,
            inline=self.inline,
            name=self.name,
            on_exit=self.on_exit,
            template=self.template,
            template_ref=self.template_ref,
            when=self.when,
            with_items=self.with_items,
            with_param=self.with_param,
            with_sequence=self.with_sequence,
        )
