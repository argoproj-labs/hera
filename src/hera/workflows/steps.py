"""The `hera.workflows.steps` module provides the Steps, Step and Parallel classes.

See <https://argoproj.github.io/argo-workflows/walk-through/steps>
for more on Steps.
"""

from typing import Any, List, Optional, Set, Union

from hera.shared._pydantic import PrivateAttr
from hera.workflows._context import _context
from hera.workflows._meta_mixins import CallableTemplateMixin, ContextMixin
from hera.workflows._mixins import (
    ArgumentsMixin,
    IOMixin,
    ItemMixin,
    ParameterMixin,
    SubNodeMixin,
    TemplateInvocatorSubNodeMixin,
    TemplateMixin,
)
from hera.workflows.exceptions import InvalidType, NodeNameConflict
from hera.workflows.models import (
    ParallelSteps,
    Template as _ModelTemplate,
    WorkflowStep as _ModelWorkflowStep,
)
from hera.workflows.protocol import Steppable, Templatable


class DummyContext:
    def __enter__(self):
        pass

    def __exit__(self, *_):
        pass


def parallel():
    """Open a parallel context within a steps-decorator function.

    When running locally, the context will be a no-op.
    """
    if _context.declaring:
        return Parallel()

    return DummyContext()


class Step(
    TemplateInvocatorSubNodeMixin,
    ArgumentsMixin,
    ParameterMixin,
    ItemMixin,
):
    """A step runs a given template.

    It must be instantiated under a Steps or Parallel context, or outside a Workflow.
    """

    @property
    def _subtype(self) -> str:
        return "steps"

    def _build_as_workflow_step(self) -> _ModelWorkflowStep:
        _template = None
        if isinstance(self.template, str):
            _template = self.template
        elif isinstance(self.template, (_ModelTemplate, TemplateMixin)):
            _template = self.template.name

        _inline = None
        if isinstance(self.inline, _ModelTemplate):
            _inline = self.inline
        elif isinstance(self.inline, Templatable):
            _inline = self.inline._build_template()

        return _ModelWorkflowStep(
            arguments=self._build_arguments(),
            continue_on=self.continue_on,
            hooks=self.hooks,
            inline=_inline,
            name=self.name,
            on_exit=self._build_on_exit(),
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
    """Parallel is a context manager used to create a list of steps to run in parallel.

    Parallel implements the context manager interface so allows usage of `with`, under which any
    `hera.workflows.steps.Step` objects instantiated will be added to Parallel's list of sub_steps.
    """

    sub_steps: List[Union[Step, _ModelWorkflowStep]] = []

    _node_names = PrivateAttr(default_factory=set)

    def _add_sub(self, node: Any):
        if isinstance(node, Templatable):
            from hera.workflows.workflow import Workflow

            # We must be under a workflow context due to checks in _HeraContext.add_sub_node
            assert _context.pieces and isinstance(_context.pieces[0], Workflow)
            _context.pieces[0]._add_sub(node)
            return

        if not isinstance(node, Step):
            raise InvalidType(type(node))
        if node.name in self._node_names:
            raise NodeNameConflict(f"Found multiple Steps named: {node.name}")
        self._node_names.add(node.name)
        self.sub_steps.append(node)

    def _build_step(self) -> List[_ModelWorkflowStep]:
        steps = []
        for step in self.sub_steps:
            if isinstance(step, Step):
                steps.append(step._build_as_workflow_step())
            elif isinstance(step, _ModelWorkflowStep):
                steps.append(step)
            else:
                raise InvalidType(type(step))
        return steps


class Steps(
    IOMixin,
    TemplateMixin,
    CallableTemplateMixin,
    ContextMixin,
):
    """A Steps template invocator is used to define a sequence of steps which can run sequentially or in parallel.

    Steps implements the contextmanager interface so allows usage of `with`, under which any
    `hera.workflows.steps.Step` objects instantiated will be added to the Steps' list of sub_steps.

    * Step and Parallel objects initialised within a Steps context will be added to the list of sub_steps
    in the order they are initialised.
    * All Step objects initialised within a Parallel context will run in parallel.
    """

    _node_names: Set[str] = PrivateAttr(default_factory=set)

    sub_steps: List[
        Union[
            Step,
            Parallel,
            List[Step],
            _ModelWorkflowStep,
            List[_ModelWorkflowStep],
        ]
    ] = []

    def _build_steps(self) -> Optional[List[ParallelSteps]]:
        steps = []
        for workflow_step in self.sub_steps:
            if isinstance(workflow_step, Steppable):
                steps.append(ParallelSteps(__root__=workflow_step._build_step()))
            elif isinstance(workflow_step, _ModelWorkflowStep):
                steps.append(ParallelSteps(__root__=[workflow_step]))
            elif isinstance(workflow_step, List):
                substeps = []
                for s in workflow_step:
                    if isinstance(s, Step):
                        substeps.append(s._build_as_workflow_step())
                    elif isinstance(s, _ModelWorkflowStep):
                        substeps.append(s)
                    else:
                        raise InvalidType(type(s))
                steps.append(ParallelSteps(__root__=substeps))
            else:
                raise InvalidType(type(workflow_step))

        return steps or None

    def _add_sub(self, node: Any):
        if isinstance(node, Templatable):
            from hera.workflows.workflow import Workflow

            # We must be under a workflow context due to checks in _HeraContext.add_sub_node
            assert _context.pieces and isinstance(_context.pieces[0], Workflow)
            _context.pieces[0]._add_sub(node)
            return

        if not isinstance(node, (Step, Parallel)):
            raise InvalidType(type(node))
        if isinstance(node, Step):
            if node.name in self._node_names:
                raise NodeNameConflict(f"Found multiple Step nodes with name: {node.name}")
            self._node_names.add(node.name)
        if isinstance(node, Parallel):
            node._node_names = self._node_names
        self.sub_steps.append(node)

    def parallel(self) -> Parallel:
        """Returns a Parallel object which can be used in a sub-context manager."""
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
            init_containers=self._build_init_containers(),
            inputs=self._build_inputs(),
            memoize=self.memoize,
            metadata=self._build_metadata(),
            metrics=self._build_metrics(),
            name=self.name,
            node_selector=self.node_selector,
            outputs=self._build_outputs(),
            parallelism=self.parallelism,
            plugin=self.plugin,
            pod_spec_patch=self.pod_spec_patch,
            priority_class_name=self.priority_class_name,
            resource=None,
            retry_strategy=self._build_retry_strategy(),
            scheduler_name=self.scheduler_name,
            script=None,
            security_context=self.pod_security_context,
            service_account_name=self.service_account_name,
            sidecars=self._build_sidecars(),
            steps=self._build_steps(),
            suspend=None,
            synchronization=self.synchronization,
            timeout=self.timeout,
            tolerations=self.tolerations,
        )


__all__ = [
    "Steps",
    "Step",
    "Parallel",
    "parallel",
]
