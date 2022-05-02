from enum import Enum


class RetryPolicy(str, Enum):
    """A representation of the retry policy for a task.

    Use retryPolicy to choose which failures to retry:

      * Always: Retry all failed steps
      * OnFailure: Retry steps whose main container is marked as failed in Kubernetes
      * OnError: Retry steps that encounter Argo controller errors, or whose init or wait containers fail
      * OnTransientError: Retry steps that encounter errors defined as transient, or errors matching the
        TRANSIENT_ERROR_PATTERN environment variable. Available in version 3.0 and later.
    """

    Always = "Always"
    OnFailure = "OnFailure"
    OnError = "OnError"
    OnTransientError = "OnTransientError"
