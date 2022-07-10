import threading
from typing import Optional, Union

from hera.cron_workflow import CronWorkflow
from hera.workflow import Workflow
from hera.workflow_template import WorkflowTemplate


class _Context(threading.local):
    def __init__(self) -> None:
        super().__init__()
        self.workflow: Optional[Union[Workflow, CronWorkflow, WorkflowTemplate]] = None


context = _Context()
