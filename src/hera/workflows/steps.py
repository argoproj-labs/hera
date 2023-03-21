from operator import xor
from typing import Any, Dict, List, Optional, Union

from pydantic import root_validator

from hera.workflows._mixins import (
    ArgumentsMixin,
    ContextMixin,
    IOMixin,
    ItemMixin,
    ParameterMixin,
    SubNodeMixin,
    TemplateMixin,
)
from hera.workflows.exceptions import InvalidType
from hera.workflows.models import (
    ContinueOn as _ModelContinueOn,
    LifecycleHook as _ModelLifecycleHook,
    Sequence as _ModelSequence,
    Template as _ModelTemplate,
    TemplateRef as _ModelTemplateRef,
    WorkflowStep as _ModelWorkflowStep,
)
from hera.workflows.protocol import Steppable


class Step(
    ArgumentsMixin,
    SubNodeMixin,
    ParameterMixin,
    ItemMixin,
):
    continue_on: Optional[_ModelContinueOn]
    hooks: Optional[Dict[str, _ModelLifecycleHook]]
    inline: Optional[_ModelTemplate]
    name: Optional[str]
    on_exit: Optional[str]
    template: Optional[Union[str, _ModelTemplate, TemplateMixin]]
    template_ref: Optional[_ModelTemplateRef]
    when: Optional[str]
    with_sequence: Optional[_ModelSequence]

    @root_validator(pre=False)
    def _check_values(cls, values):
        if not xor(bool(values.get("template")), bool(values.get("template_ref"))):
            raise ValueError("exactly one of ['template', 'template_ref'] must be present")
        return values

    @property
    def id(self) -> str:
        return f"{{{{steps.{self.name}.id}}}}"

    @property
    def ip(self) -> str:
        return f"{{{{steps.{self.name}.ip}}}}"

    @property
    def status(self) -> str:
        return f"{{{{steps.{self.name}.status}}}}"

    @property
    def exit_code(self) -> str:
        return f"{{{{steps.{self.name}.exitCode}}}}"

    @property
    def started_at(self) -> str:
        return f"{{{{steps.{self.name}.startedAt}}}}"

    @property
    def finished_at(self) -> str:
        return f"{{{{steps.{self.name}.finishedAt}}}}"

    @property
    def result(self) -> str:
        return f"{{{{steps.{self.name}.outputs.result}}}}"

    def _build_as_workflow_step(self) -> _ModelWorkflowStep:
        _template = None
        if isinstance(self.template, str):
            _template = self.template
        elif isinstance(self.template, (_ModelTemplate, TemplateMixin)):
            _template = self.template.name

        return _ModelWorkflowStep(
            arguments=self._build_arguments(),
            continue_on=self.continue_on,
            hooks=self.hooks,
            inline=self.inline,
            name=self.name,
            on_exit=self.on_exit,
            template=_template,
            template_ref=self.template_ref,
            when=self.when,
            with_items=self._build_with_items(),
            with_param=self._build_with_param(),
            with_sequence=self.with_sequence,
        )

    def _build_step(
        self,
    ) -> List[_ModelWorkflowStep]:
        return [self._build_as_workflow_step()]


class Parallel(
    ContextMixin,
    SubNodeMixin,
):
    sub_steps: List[Union[Step, _ModelWorkflowStep]] = []

    def _add_sub(self, node: Any):
        if not isinstance(node, Step):
            raise InvalidType()
        self.sub_steps.append(node)

    def _build_step(self) -> List[_ModelWorkflowStep]:
        steps = []
        for step in self.sub_steps:
            if isinstance(step, Step):
                steps.append(step._build_as_workflow_step())
            elif isinstance(step, _ModelWorkflowStep):
                steps.append(step)
            else:
                raise InvalidType()
        return steps


class Steps(
    ContextMixin,
    IOMixin,
    TemplateMixin,
):
    sub_steps: List[
        Union[
            Step,
            Parallel,
            List[Step],
            _ModelWorkflowStep,
            List[_ModelWorkflowStep],
        ]
    ] = []

    def _build_steps(self) -> Optional[List[List[_ModelWorkflowStep]]]:
        steps = []
        for workflow_step in self.sub_steps:
            if isinstance(workflow_step, Steppable):
                steps.append(workflow_step._build_step())
            elif isinstance(workflow_step, _ModelWorkflowStep):
                steps.append([workflow_step])
            elif isinstance(workflow_step, List):
                substeps = []
                for s in workflow_step:
                    if isinstance(s, Step):
                        substeps.append(s._build_as_workflow_step())
                    elif isinstance(s, _ModelWorkflowStep):
                        substeps.append(s)
                    else:
                        raise InvalidType()
                steps.append(substeps)
            else:
                raise InvalidType()

        return steps or None

    def _add_sub(self, node: Any):
        if not isinstance(node, (Step, Parallel)):
            raise InvalidType()

        self.sub_steps.append(node)

    def parallel(self) -> Parallel:
        return Parallel()

    def _build_template(self) -> _ModelTemplate:
        return _ModelTemplate(
            active_deadline_seconds=self.active_deadline_seconds,
            affinity=self.affinity,
            archive_location=self.archive_location,
            automount_service_account_token=self.automount_service_account_token,
            container=None,
            container_set=None,
            daemon=self.daemon,
            dag=None,
            data=None,
            executor=self.executor,
            fail_fast=self.fail_fast,
            http=None,
            host_aliases=self.host_aliases,
            init_containers=self.init_containers,
            inputs=self._build_inputs(),
            memoize=self.memoize,
            metadata=self._build_metadata(),
            metrics=self.metrics,
            name=self.name,
            node_selector=self.node_selector,
            outputs=self._build_outputs(),
            parallelism=self.parallelism,
            plugin=self.plugin,
            pod_spec_patch=self.pod_spec_patch,
            priority=self.priority,
            priority_class_name=self.priority_class_name,
            resource=None,
            retry_strategy=self.retry_strategy,
            scheduler_name=self.scheduler_name,
            script=None,
            security_context=self.pod_security_context,
            service_account_name=self.service_account_name,
            sidecars=self.sidecars,
            steps=self._build_steps(),
            suspend=None,
            synchronization=self.synchronization,
            timeout=self.timeout,
            tolerations=self.tolerations,
        )


__all__ = ["Steps", "Step", "Parallel"]
