from typing import Any, List, Optional, Union

from hera.workflows.models import (
    ParallelSteps as _ModelParallelSteps,
    Template as _ModelTemplate,
    WorkflowStep as _ModelWorkflowStep,
)
from hera.workflows.v5._mixins import (
    _ContextMixin,
    _IOMixin,
    _SubNodeMixin,
    _TemplateMixin,
)
from hera.workflows.v5.exceptions import InvalidType
from hera.workflows.v5.protocol import Steppable


class Step(
    _ModelWorkflowStep,
    _SubNodeMixin,
):
    def _build_step(
        self,
    ) -> _ModelWorkflowStep:
        return _ModelWorkflowStep(
            arguments=self.arguments,
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


class Steps(
    _ContextMixin,
    _IOMixin,
    _SubNodeMixin,
    _TemplateMixin,
):
    workflow_steps: List[Union[_ModelParallelSteps, _ModelWorkflowStep]] = []

    def _build_steps(self) -> Optional[List[_ModelParallelSteps]]:
        steps = []
        for steppable in self.workflow_steps:
            if isinstance(steppable, _ModelParallelSteps):
                steps.append(steppable)
            elif isinstance(steppable, _ModelWorkflowStep):
                steps.append([steppable])

        return steps or None

    def _add_sub(self, node: Any):
        if not isinstance(node, Steppable):
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
