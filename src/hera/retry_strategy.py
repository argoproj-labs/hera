from enum import Enum
from typing import Optional, Union

from pydantic import root_validator

from hera.models import Backoff, RetryAffinity
from hera.models import RetryStrategy as _ModelRetryStrategy


class RetryPolicy(Enum):
    """A representation of the retry policy for a task.

    Use retryPolicy to choose which failures to retry:

      * Always: Retry all failed steps
      * OnFailure: Retry steps whose main container is marked as failed in Kubernetes
      * OnError: Retry steps that encounter Argo controller errors, or whose init or wait containers fail
      * OnTransientError: Retry steps that encounter errors defined as transient, or errors matching the
        TRANSIENT_ERROR_PATTERN environment variable. Available in version 3.0 and later.
    """

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


class RetryStrategy(_ModelRetryStrategy):
    affinity: Optional[RetryAffinity] = None  # type: ignore
    backoff: Optional[Backoff] = None  # type: ignore
    expression: Optional[str] = None  # type: ignore
    limit: Optional[Union[int, str]] = None  # type: ignore
    retry_policy: Optional[Union[str, RetryPolicy]] = None  # type: ignore

    @root_validator(pre=True)
    def _check_values(cls, values):
        if values.get("retry_policy") and isinstance(values.get("retry_policy"), RetryPolicy):
            values["retry_policy"] = str(values.get("retry_policy"))
        return values


__all__ = ["RetryPolicy", "RetryStrategy"]
