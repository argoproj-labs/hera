from enum import Enum


class VolumeClaimGCStrategy(Enum):
    """A representation of the strategy to use when deleting volumes from completed workflows

    Notes
    -----
        See sdk doc (IoArgoprojWorkflowV1alpha1VolumeClaimGC)
    """

    OnWorkflowCompletion = "OnWorkflowCompletion"
    """delete volume claim when workflow is completed
    """

    OnWorkflowSuccess = "OnWorkflowSuccess"
    """delete volume claim when workflow is successful
    """
