from typing import Any, Dict, List, Optional, Union

from hera.workflows.models import (
    Arguments as _ModelArguments,
    Artifact as _ModelArtifact,
    ContinueOn as _ModelContinueOn,
    Item as _ModelItem,
    LifecycleHook as _ModelLifecycleHook,
    Parameter as _ModelParameter,
    Sequence as _ModelSequence,
    Template as _ModelTemplate,
    TemplateRef as _ModelTemplateRef,
    WorkflowStep as _ModelWorkflowStep,
)
from hera.workflows.v5._mixins import (
    _ContextMixin,
    _IOMixin,
    _SubNodeMixin,
    _TemplateMixin,
)
from hera.workflows.v5.exceptions import InvalidType


class Step(
    _SubNodeMixin,
):
    arguments: Optional[List[Union[_ModelArtifact, _ModelParameter]]] = None
    continue_on: Optional[_ModelContinueOn]
    hooks: Optional[Dict[str, _ModelLifecycleHook]]
    inline: Optional[_ModelTemplate]
    name: Optional[str]
    on_exit: Optional[str]
    template: Optional[str]
    template_ref: Optional[_ModelTemplateRef]
    when: Optional[str]
    with_items: Optional[List[_ModelItem]]
    with_param: Optional[str]
    with_sequence: Optional[_ModelSequence]

    def _build_as_workflow_step(self) -> _ModelWorkflowStep:
        # Convert the unified list of Artifacts and Parameters in self.arguments to a
        # model-class Arguments to pass to WorkflowStep
        _arguments = _ModelArguments(
            artifacts=list(filter(lambda arg: isinstance(arg, _ModelArtifact), self.arguments or [])) or None,
            parameters=list(filter(lambda arg: isinstance(arg, _ModelParameter), self.arguments or [])) or None,
        )

        return _ModelWorkflowStep(
            arguments=_arguments,
            continue_on=self.continue_on,
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

    def _build_as_parallel_steps(
        self,
    ) -> List[_ModelWorkflowStep]:
        return [self._build_as_workflow_step()]


class ParallelSteps(
    _ContextMixin,
    _SubNodeMixin,
):
    parallel_steps: List[Step] = []

    def _add_sub(self, node: Any):
        if not isinstance(node, Step):
            raise InvalidType()
        self.parallel_steps.append(node)

    def _build_as_parallel_steps(self) -> List[_ModelWorkflowStep]:
        return [step._build_as_workflow_step() for step in self.parallel_steps]


class Steps(
    _ContextMixin,
    _IOMixin,
    _SubNodeMixin,
    _TemplateMixin,
):
    workflow_steps: List[Union[Step, ParallelSteps]] = []

    def _build_steps(self) -> Optional[List[List[_ModelWorkflowStep]]]:
        steps = []
        for workflow_step in self.workflow_steps:
            steps.append(workflow_step._build_as_parallel_steps())

        return steps or None

    def _add_sub(self, node: Any):
        if not isinstance(node, (Step, ParallelSteps)):
            raise InvalidType()

        self.workflow_steps.append(node)

    def _build_template(self) -> _ModelTemplate:
        return _ModelTemplate(
            active_deadline_seconds=self.active_deadline_seconds,
            affinity=self.affinity,
            archive_location=self.archive_location,
            automount_service_account_token=self.automount_service_account_token,
            daemon=self.daemon,
            executor=self.executor,
            fail_fast=self.fail_fast,
            host_aliases=self.host_aliases,
            init_containers=self.init_containers,
            inputs=self._build_inputs(),
            memoize=self.memoize,
            metadata=self._build_metadata(),
            metrics=self.metrics,
            name=self.name,
            node_selector=self.node_selector,
            outputs=self._build_outputs(),
            plugin=self.plugin,
            pod_spec_patch=self.pod_spec_patch,
            priority=self.priority,
            priority_class_name=self.priority_class_name,
            retry_strategy=self.retry_strategy,
            scheduler_name=self.scheduler_name,
            security_context=self.pod_security_context,
            service_account_name=self.service_account_name,
            sidecars=self.sidecars,
            steps=self._build_steps(),
            synchronization=self.synchronization,
            timeout=self.timeout,
            tolerations=self.tolerations,
        )
