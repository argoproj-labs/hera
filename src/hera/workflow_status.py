from enum import Enum


class WorkflowStatus(str, Enum):
    """Placeholder for workflow statuses"""

    Running = 'Running'
    Succeeded = 'Succeeded'
    Failed = 'Failed'
    Error = 'Error'
    Terminated = 'Terminated'

    @classmethod
    def from_argo_status(cls, s: str) -> 'WorkflowStatus':
        """Turns an Argo status into a Dyno workflows representation"""
        switch = {
            'Running': WorkflowStatus.Running,
            'Succeeded': WorkflowStatus.Succeeded,
            'Failed': WorkflowStatus.Failed,
            'Error': WorkflowStatus.Error,
            'Terminated': WorkflowStatus.Terminated,
        }
        return switch.get(s)
