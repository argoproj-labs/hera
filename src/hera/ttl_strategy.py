from typing import Optional

from argo_workflows.models import IoArgoprojWorkflowV1alpha1TTLStrategy
from pydantic import BaseModel


class TTLStrategy(BaseModel):
    """TTLStrategy specification for workflows.

    https://argoproj.github.io/argo-workflows/fields/#ttlstrategy

    Automatically delete workflows after a specified period of time after
    the workflow completes/fails/succeeds.

    Attributes
    ----------
    seconds_after_completion: int
        The number of seconds to live after completion.
    seconds_after_failure: int
        The number of seconds to live after failure.
    seconds_after_success: int
        The number of seconds to live after success.

    """

    seconds_after_completion: Optional[int]
    seconds_after_failure: Optional[int]
    seconds_after_success: Optional[int]

    @property
    def argo_ttl_strategy(self) -> IoArgoprojWorkflowV1alpha1TTLStrategy:
        """Constructs and returns the ttl strategy"""
        return IoArgoprojWorkflowV1alpha1TTLStrategy(
            seconds_after_completion=self.seconds_after_completion,
            seconds_after_failure=self.seconds_after_failure,
            seconds_after_success=self.seconds_after_success,
        )
