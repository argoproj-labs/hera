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
    ContextMixin,
    IOMixin,
    SubNodeMixin,
    TemplateMixin,
)
from hera.workflows.v5.exceptions import InvalidType
from hera.workflows.v5.protocol import Steppable


class Step(
    SubNodeMixin,
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
        # model-class `Arguments`` to pass to WorkflowStep
        artifacts = list(filter(lambda arg: isinstance(arg, _ModelArtifact), self.arguments or []))
        parameters = list(filter(lambda arg: isinstance(arg, _ModelParameter), self.arguments or []))
        model_arguments = _ModelArguments(
            artifacts=None if len(artifacts) == 0 else artifacts,
            parameters=None if len(parameters) == 0 else parameters,
        )
        arguments = (
            None if model_arguments.artifacts is None and model_arguments.parameters is None else model_arguments
        )
        return _ModelWorkflowStep(
            arguments=arguments,
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
