from typing import Optional

from pydantic import BaseModel, root_validator


class Retry(BaseModel):
    """Retry holds the duration values for retrying tasks.

    Attributes
    ----------
    duration: int
        The duration (seconds) is the amount to back off between retries.
    max_duration: int
        Max duration (seconds) is the maximum amount of time allowed for the backoff strategy. This value is
        expected to be higher than the specified duration. Not specifying this value leads to theoretically infinite
        retries.
    """

    duration: int
    max_duration: Optional[int]

    @root_validator()
    def check_durations(cls, values):
        duration: int = values.get('duration')
        max_duration: int = values.get('max_duration')
        if max_duration is not None:
            assert duration <= max_duration, 'duration cannot be greater than the max duration'
        return values
