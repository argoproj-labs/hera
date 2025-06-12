"""The `hera.workflows.workflow_status` module provides lightweight functionality for representing and interacting with workflow statuses.

See the [Workflow Status example](../../../examples/workflows/misc/workflow_on_exit.md) for usage.
"""

from enum import Enum


class WorkflowStatus(str, Enum):
    """Placeholder for workflow statuses."""

    running = "Running"
    succeeded = "Succeeded"
    failed = "Failed"
    error = "Error"
    terminated = "Terminated"

    def __str__(self) -> str:
        """Returns the value representation of the workflow status enum."""
        return str(self.value)

    @classmethod
    def from_argo_status(cls, s: str) -> "WorkflowStatus":
        """Turns an Argo status into a Hera workflow status representation."""
        switch = {
            "Running": WorkflowStatus.running,
            "Succeeded": WorkflowStatus.succeeded,
            "Failed": WorkflowStatus.failed,
            "Error": WorkflowStatus.error,
            "Terminated": WorkflowStatus.terminated,
        }

        ss = switch.get(s)
        if not ss:
            raise KeyError(f"Unrecognized status {s}. Available Argo statuses are: {list(switch.keys())}")
        return ss


__all__ = ["WorkflowStatus"]
