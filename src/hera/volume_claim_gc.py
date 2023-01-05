from enum import Enum


class VolumeClaimGCStrategy(Enum):
    """A representation of the strategy to use when deleting volumes from completed workflows"""

    on_workflow_completion = "OnWorkflowCompletion"
    """delete volume claim when workflow is completed"""

    on_workflow_success = "OnWorkflowSuccess"
    """delete volume claim when workflow is successful"""

    def __str__(self):
        return str(self.value)
