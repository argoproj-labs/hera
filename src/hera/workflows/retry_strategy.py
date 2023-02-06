from dataclasses import dataclass
from typing import Optional, Union

from argo_workflows.models import IoArgoprojWorkflowV1alpha1RetryStrategy

from hera.backoff import Backoff
from hera.retry_policy import RetryPolicy


@dataclass
class RetryStrategy:
    """Retry holds the duration values for retrying tasks.

    Attributes
    ----------
    backoff: Optional[Backoff] = None
        Backoff strategy. See `hera.backoff.Backoff` or https://argoproj.github.io/argo-workflows/fields/#backoff.
    expression: Optional[str] = None
        Expression is a condition expression for when a node will be retried.
        If it evaluates to false, the node will not be retried and the retry strategy will be ignored
    limit: Optional[Union[int, str]] = None
        The number of retries to attempt.
    retry_policy: RetryPolicy
        The strategy for performing retries, for example OnError vs OnFailure vs Always
    """

    backoff: Optional[Backoff] = None
    expression: Optional[str] = None
    limit: Optional[Union[int, str]] = None
    retry_policy: RetryPolicy = RetryPolicy.Always

    def __post_init__(self):
        if self.limit is not None and isinstance(self.limit, int):
            self.limit = str(self.limit)

    def build(self) -> IoArgoprojWorkflowV1alpha1RetryStrategy:
        strategy = IoArgoprojWorkflowV1alpha1RetryStrategy()
        if self.backoff is not None:
            setattr(strategy, "backoff", self.backoff.build())
        if self.expression is not None:
            setattr(strategy, "expression", self.expression)
        if self.limit is not None:
            setattr(strategy, "limit", self.limit)
        if self.retry_policy is not None:
            setattr(strategy, "retry_policy", str(self.retry_policy.value))

        return strategy
