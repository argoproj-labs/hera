from dataclasses import dataclass
from typing import Optional

from hera.retry_policy import RetryPolicy


@dataclass
class Retry:
    """Retry holds the duration values for retrying tasks.

    Attributes
    ----------
    duration: int
        The duration (seconds) is the amount to back off between retries.
    max_duration: int
        Max duration (seconds) is the maximum amount of time allowed for the backoff strategy. This value is
        expected to be higher than the specified duration. Not specifying this value leads to theoretically infinite
        retries.
    limit: int
        The number of retries to attempt
    retry_policy: RetryPolicy
        The strategy for performing retries, for example OnError vs OnFailure vs Always
    """

    duration: Optional[int] = None
    limit: Optional[int] = None
    max_duration: Optional[int] = None
    retry_policy: Optional[RetryPolicy] = RetryPolicy.Always

    def __post_init__(self):
        self.validate_durations()

    def validate_durations(self):
        if self.max_duration and self.duration:
            assert self.duration <= self.max_duration, "duration cannot be greater than the max duration"
