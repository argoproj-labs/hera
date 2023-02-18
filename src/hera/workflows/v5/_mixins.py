from __future__ import annotations

from typing import Dict, List, Optional, Union, cast

from pydantic import validator

from hera.workflows._base_model import BaseModel as _BaseModel
from hera.workflows.models import (
    HTTP,
    Affinity,
    Arguments,
    Artifact,
    ArtifactLocation,
    ContainerPort,
    ContinueOn,
    DAGTask,
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
    TemplateRef,
    TerminationMessagePolicy,
    Toleration,
)
from hera.workflows.models import UserContainer as ModelUserContainer
from hera.workflows.models import VolumeDevice, VolumeMount
from hera.workflows.v5.env import _BaseEnv
from hera.workflows.v5.env_from import _BaseEnvFrom
from hera.workflows.v5.operator import Operator
from hera.workflows.v5.parameter import Parameter
from hera.workflows.v5.resources import Resources
from hera.workflows.v5.task_result import TaskResult
from hera.workflows.v5.user_container import UserContainer
from hera.workflows.v5.volume import _BaseVolume
from hera.workflows.v5.workflow_status import WorkflowStatus

Inputs = List[Union[Artifact, Parameter, ModelParameter]]
Outputs = List[Union[Artifact, Parameter, ModelParameter]]


class _BaseMixin(_BaseModel):
    pass


class _ContainerMixin(_BaseMixin):
    image: str
    image_pull_policy: Optional[Union[str, ImagePullPolicy]] = None

    @validator('image_pull_policy', pre=True)
    def _convert_image_pull_policy(cls, v):
        if v is None or isinstance(v, ImagePullPolicy):
            return v
        v = cast(str, v)
        return ImagePullPolicy[v.lower()]  # must be str


class _IOMixin(_BaseMixin):
    inputs: Optional[Union[Inputs, ModelInputs]] = None
    outputs: Optional[Union[Outputs, ModelOutputs]] = None

    def build_inputs(self) -> Optional[ModelInputs]:
        if self.inputs is None:
            return None

        result = ModelInputs()
        if isinstance(self.inputs, list):
            for value in self.inputs:
                if isinstance(value, Artifact):
                    result.artifacts = [value] if result.artifacts is None else result.artifacts + [value]
                elif isinstance(value, Parameter):
                    result.parameters = (
                        [value.as_input()] if result.parameters is None else result.parameters + [value.as_input()]
                    )
                else:
                    result.parameters = [value] if result.parameters is None else result.parameters + [value]
        return cast(ModelInputs, self.inputs)

    def build_outputs(self) -> Optional[ModelOutputs]:
        if self.outputs is None:
            return None

        result = ModelOutputs()
        if isinstance(self.outputs, list):
            for value in self.outputs:
                if isinstance(value, Artifact):
                    result.artifacts = [value] if result.artifacts is None else result.artifacts + [value]
                elif isinstance(value, Parameter):
                    result.parameters = (
                        [value.as_output()] if result.parameters is None else result.parameters + [value.as_output()]
                    )
                else:
                    result.parameters = [value] if result.parameters is None else result.parameters + [value]
        return cast(ModelOutputs, self.outputs)


class _EnvMixin(_BaseMixin):
    env: Optional[List[Union[_BaseEnv, EnvVar]]] = None
    env_from: Optional[List[Union[_BaseEnvFrom, EnvFromSource]]] = None

    def build_end(self) -> Optional[EnvVar]:
        if self.env is None or isinstance(self.env, EnvVar):
            return self.env

        v = cast(_BaseEnv, self.env)
        return v.build()

    def build_env_from(self) -> Optional[EnvFromSource]:
        if self.env_from is None or isinstance(self.env_from, EnvFromSource):
            return self.env_from

        v = cast(_BaseEnvFrom, self.env_from)
        return v.build()


class _TemplateMixin(_BaseMixin):
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
    metadata: Optional[Metadata] = None
    metrics: Optional[Metrics] = None
    node_selector: Optional[Dict[str, str]] = None
    http: Optional[HTTP] = None
    plugin: Optional[Plugin] = None
    pod_spec_patch: Optional[str] = None
    priority: Optional[int] = None
    priority_class_name: Optional[str] = None
    retry_strategy: Optional[RetryStrategy] = None
    scheduler_name: Optional[str] = None
    liveness_probe: Optional[Probe] = None
    ports: Optional[List[ContainerPort]] = None
    readiness_probe: Optional[Probe] = None
    template_security_context: Optional[PodSecurityContext] = None
    startup_probe: Optional[Probe] = None
    stdin: Optional[bool] = None
    stdin_once: Optional[bool] = None
    termination_message_path: Optional[str] = None
    termination_message_policy: Optional[TerminationMessagePolicy] = None
    tty: Optional[bool] = None
    service_account_name: Optional[str] = None
    sidecars: Optional[List[UserContainer]] = None
    synchronization: Optional[Synchronization] = None
    timeout: Optional[str] = None
    tolerations: Optional[List[Toleration]] = None


class _ResourceMixin(_BaseMixin):
    resources: Optional[Union[ResourceRequirements, Resources]] = None

    @validator('resources', pre=True)
    def _convert_resources(cls, v):
        if v is None or isinstance(v, ResourceRequirements):
            return v

        v = cast(Resources, v)
        return v.build()


class _VolumeMountMixin(_BaseMixin):
    volume_devices: Optional[List[VolumeDevice]] = None
    volume_mounts: Optional[List[VolumeMount]] = None
    volumes: Optional[List[_BaseVolume]] = None

    @validator('volume_mounts', pre=True)
    def _convert_volumes(cls, v, values):
        volumes: Optional[List[_BaseVolume]] = values.get('volumes')
        if v is None and volumes is None:
            return None

        result = None if volumes is None else [vol.to_mount() for vol in volumes]
        if v is None:
            return result
        return v + result


class _DAGTaskMixin(_BaseMixin):
    name: str
    continue_on: Optional[ContinueOn] = None
    dependencies: Optional[List[str]] = None
    depends: Optional[str] = None
    hooks: Optional[Dict[str, LifecycleHook]]
    on_exit: Optional[str] = None
    template: Optional[str] = None
    template_ref: Optional[TemplateRef] = None
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

