from typing import List, Union

from hera.workflows.models import (
    Template,
    WorkflowStep as _ModelWorkflowStep,
)
from hera.workflows.v5._mixins import _ContextMixin
from hera.workflows.v5.protocol import Templatable


# flip_coin = Script('flip-coin', source=my_func, ...)
# heads = Container('heads', ...)
# tails = Container('tails', ...)

# with Steps('coinflip') as s:
#     flip_coin(...)
#     with ParallelStep() as s2:
#         heads(...)
#         tails(...)

# when a step is declared under a `with Steps` it should usually be referencing
# an existing template - here the "flip_coin(...)" call is adding the Script as
# a reference to the eventual "steps" member in the yaml

# In the Argo spec, a "steps" member of a "template" is of type Array<Array<WorkflowStep>> https://argoproj.github.io/argo-workflows/fields/#template
# A WorkflowStep is defined here https://argoproj.github.io/argo-workflows/fields/#workflowstep
# So under a `with Steps`, the calls on Templates should result in adding a WorkflowStep to our Steps class

class Steps(_ContextMixin):
    workflow_steps: List[_ModelWorkflowStep] = []

    def build(self) -> List[_ModelWorkflowStep]:
        return self.workflow_steps

    def _add_sub(self, node: Any):
        if not isinstance(node, _ModelWorkflowStep):
            raise InvalidType()
        self.workflow_steps.append(node)
