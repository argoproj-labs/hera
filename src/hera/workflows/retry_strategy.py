from enum import Enum
from typing import Optional, Union, cast

from pydantic import validator

from hera.shared._base_model import BaseModel as _BaseModel
from hera.workflows.models import (
    Backoff,
    IntOrString,
    RetryAffinity,
    RetryStrategy as _ModelRetryStrategy,
)


class RetryPolicy(Enum):
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

    def __str__(self):
        return str(self.value)


class RetryStrategy(_BaseModel):
    affinity: Optional[RetryAffinity] = None
    backoff: Optional[Backoff] = None
    expression: Optional[str] = None
    limit: Optional[Union[str, int, IntOrString]] = None
    retry_policy: Optional[Union[str, RetryPolicy]] = None

    @validator("retry_policy", pre=True)
    def _convert_retry_policy(cls, v):
        if v is None or isinstance(v, str):
            return v

        v = cast(RetryPolicy, v)
        return v.value

    @validator("limit", pre=True)
    def _convert_limit(cls, v):
        if v is None or isinstance(v, IntOrString):
            return v

        return str(v)  # int or str

    def build(self) -> _ModelRetryStrategy:
        return _ModelRetryStrategy(
            affinity=self.affinity,
            backoff=self.backoff,
            expression=self.expression,
            limit=self.limit,
            retry_policy=self.retry_policy,
        )


__all__ = ["RetryPolicy", "RetryStrategy"]
