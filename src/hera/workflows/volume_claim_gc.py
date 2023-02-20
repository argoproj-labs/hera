from enum import Enum


class VolumeClaimGCStrategy(str, Enum):
    """A representation of the strategy to use when deleting volumes from completed workflows"""

    OnWorkflowCompletion = "OnWorkflowCompletion"
    """delete volume claim when workflow is completed"""

    OnWorkflowSuccess = "OnWorkflowSuccess"
    """delete volume claim when workflow is successful"""

    def __str__(self):
        return str(self.value)
