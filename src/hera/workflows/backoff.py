from dataclasses import dataclass
from typing import Optional, Union

from argo_workflows.models import IoArgoprojWorkflowV1alpha1Backoff


@dataclass
class Backoff:
    """The backoff strategy to use with a retry strategy.

    Attributes
    ----------
    duration: Optional[str] = None
        Duration is the amount to back off. Default unit is seconds, but could also be a duration (e.g. "2m", "1h").
    factor: Optional[Union[int, str]] = None
        Factor is a factor to multiply the base duration by after each failed retry.
    max_duration: Optional[str] = None
        MaxDuration is the maximum amount of time allowed for the backoff strategy.

    Notes
    -----
    See: https://argoproj.github.io/argo-workflows/fields/#backoff
    """

    duration: Optional[str] = None
    factor: Optional[Union[int, str]] = None
    max_duration: Optional[str] = None

    def __post_init__(self):
        if self.factor is not None and isinstance(self.factor, int):
            self.factor = str(self.factor)

    def build(self) -> IoArgoprojWorkflowV1alpha1Backoff:
        backoff = IoArgoprojWorkflowV1alpha1Backoff()
        if self.duration is not None:
            setattr(backoff, "duration", self.duration)
        if self.factor is not None:
            setattr(backoff, "factor", self.factor)
        if self.max_duration is not None:
            setattr(backoff, "max_duration", self.max_duration)
        return backoff
