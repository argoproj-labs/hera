from typing import Optional

from argo_workflows.models import IoArgoprojWorkflowV1alpha1SuspendTemplate


class Suspend:
    """Suspends a task/template execution by the specified period.

    Parameters
    ----------
    duration: str
        Duration is the seconds to wait before automatically resuming a template. Default unit is seconds.
        Could also be a `Duration`, e.g. "2m", "6h", "1d".
    """

    def __init__(self, duration: Optional[str] = None) -> None:
        self.duration = duration

    def build(self) -> IoArgoprojWorkflowV1alpha1SuspendTemplate:
        suspend = IoArgoprojWorkflowV1alpha1SuspendTemplate()
        if self.duration is not None:
            setattr(suspend, "duration", self.duration)
        return suspend
