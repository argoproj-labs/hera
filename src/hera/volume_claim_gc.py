from enum import Enum

from argo_workflows.models import IoArgoprojWorkflowV1alpha1VolumeClaimGC
from pydantic import BaseModel


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


class VolumeClaimGC(BaseModel):
    """VolumeClaimGC describes how to delete volumes from completed Workflows

    Notes
    -----
        See sdk doc (IoArgoprojWorkflowV1alpha1VolumeClaimGC)
    """

    strategy: VolumeClaimGCStrategy

    @property
    def argo_volume_claim_gc(self) -> IoArgoprojWorkflowV1alpha1VolumeClaimGC:
        return IoArgoprojWorkflowV1alpha1VolumeClaimGC(strategy=self.strategy.value)
