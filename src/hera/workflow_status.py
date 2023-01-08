from enum import Enum


class WorkflowStatus(Enum):
    """Placeholder for workflow statuses"""

    running = "Running"
    succeeded = "Succeeded"
    failed = "Failed"
    error = "Error"
    terminated = "Terminated"

    def __str__(self):
        return str(self.value)

    @classmethod
    def from_argo_status(cls, s: str) -> "WorkflowStatus":
        """Turns an Argo status into a Hera workflow status representation"""
        switch = {
            "running": WorkflowStatus.running,
            "succeeded": WorkflowStatus.succeeded,
            "failed": WorkflowStatus.failed,
            "error": WorkflowStatus.error,
            "terminated": WorkflowStatus.terminated,
        }

        ss = switch.get(s.lower())
        if not ss:
            raise KeyError(f"Unrecognized status {s}. " f"Available Argo statuses are: {list(switch.keys())}")
        return ss


__all__ = ["WorkflowStatus"]
