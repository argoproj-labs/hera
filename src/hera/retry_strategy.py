from dataclasses import dataclass
from typing import Dict, Optional

from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Backoff,
    IoArgoprojWorkflowV1alpha1RetryAffinity,
    IoArgoprojWorkflowV1alpha1RetryStrategy,
)

from hera.retry_policy import RetryPolicy


@dataclass
class RetryStrategy:
    """Retry holds the duration values for retrying tasks.

    Attributes
    ----------
    affinity: Optional[Dict] = None
        Affinity prevents running workflow's step on the same host.
        See: https://argoproj.github.io/argo-workflows/fields/#retryaffinity
    backoff: Optional[Dict] = None
        Backoff strategy.
        See: https://argoproj.github.io/argo-workflows/fields/#backoff
    expression: Optional[str] = None
        Expression is a condition expression for when a node will be retried.
        If it evaluates to false, the node will not be retried and the retry strategy will be ignored
    limit: Optional[int] = None
        The number of retries to attempt
    retry_policy: RetryPolicy
        The strategy for performing retries, for example OnError vs OnFailure vs Always
    """

    affinity: Optional[Dict] = None
    backoff: Optional[Dict] = None
    expression: Optional[str] = None
    limit: Optional[int] = None
    retry_policy: RetryPolicy = RetryPolicy.Always

    def build(self):
        strategy = IoArgoprojWorkflowV1alpha1RetryStrategy()
        if self.affinity is not None:
            setattr(strategy, "affinity", IoArgoprojWorkflowV1alpha1RetryAffinity(**self.affinity))
        if self.backoff is not None:
            setattr(strategy, "backoff", IoArgoprojWorkflowV1alpha1Backoff(**self.backoff))
        if self.expression is not None:
            setattr(strategy, "expression", self.expression)
        if self.limit is not None:
            setattr(strategy, "limit", str(self.limit))
        if self.retry_policy is not None:
            setattr(strategy, "retry_policy", str(self.retry_policy.value))

        return strategy
