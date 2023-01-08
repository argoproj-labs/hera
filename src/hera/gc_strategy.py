from enum import Enum


class GCStrategy(Enum):
    """A representation of the strategy to use when applying garbage collection strategies"""

    on_workflow_completion = "OnWorkflowCompletion"
    """GC when workflow is completed"""

    on_workflow_success = "OnWorkflowSuccess"
    """GC when workflow is successful"""

    on_workflow_deletion = "OnWorkflowDeletion"
    """GC when workflow is deleted"""

    def __str__(self):
        return str(self.value)


__all__ = ["GCStrategy"]
