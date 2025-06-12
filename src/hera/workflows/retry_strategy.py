"""The `hera.workflows.retry_strategy` module provides retry strategy functionality, along with necessary dependencies such as retry policy."""

from enum import Enum
from typing import Optional, Union, cast

from hera.shared._pydantic import (
    BaseModel as _BaseModel,
    validator,
)
from hera.workflows.models import (
    Backoff,
    IntOrString,
    RetryAffinity,
    RetryStrategy as _ModelRetryStrategy,
)


class RetryPolicy(Enum):
    """An enum that holds options for retry policy."""

    always = "Always"
    """Retry all failed steps"""

    on_failure = "OnFailure"
    """Retry steps whose main container is marked as failed in Kubernetes"""

    on_error = "OnError"
    """Retry steps that encounter Argo controller errors, or whose init or wait containers fail"""

    on_transient_error = "OnTransientError"
    """Retry steps that encounter errors defined as transient, or errors matching the `TRANSIENT_ERROR_PATTERN`
    environment variable.
    Available in version 3.0 and later.
    """

    def __str__(self) -> str:
        """Assembles the `value` representation of the enum as a string."""
        return str(self.value)


class RetryStrategy(_BaseModel):
    """`RetryStrategy` configures how an Argo job should retry."""

    affinity: Optional[RetryAffinity] = None
    """affinity dictates the affinity of the retried jobs"""

    backoff: Optional[Backoff] = None
    """backoff dictates how long should a job wait for before retrying"""

    expression: Optional[str] = None
    """the expression field supports the expression of complex rules regarding retry behavior"""

    limit: Optional[Union[int, str, IntOrString]] = None
    """the hard numeric limit of how many times a jobs should retry"""

    retry_policy: Optional[Union[str, RetryPolicy]] = None
    """the policy dictates, at a high level, under what conditions should a job retry"""

    @validator("retry_policy", pre=True)
    def _convert_retry_policy(cls, v):
        """Converts the `retry_policy` field into a pure `str` from either `str` already or an enum."""
        if v is None or isinstance(v, str):
            return v

        v = cast(RetryPolicy, v)
        return v.value

    @validator("limit", pre=True)
    def _convert_limit(cls, v) -> Optional[IntOrString]:
        """Converts the `limit` field from the union specification into a `str`."""
        if v is None or isinstance(v, IntOrString):
            return v

        return IntOrString(__root__=v)

    def build(self) -> _ModelRetryStrategy:
        """Builds the generated `RetryStrategy` representation of the retry strategy."""
        return _ModelRetryStrategy(
            affinity=self.affinity,
            backoff=self.backoff,
            expression=self.expression,
            limit=self.limit,  # type: ignore
            retry_policy=str(self.retry_policy) if self.retry_policy is not None else None,
        )


__all__ = ["RetryPolicy", "RetryStrategy"]
