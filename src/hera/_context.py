import threading
from typing import Optional

from hera.workflow import Workflow


class _Context(threading.local):
    def __init__(self) -> None:
        super().__init__()
        self.workflow: Optional[Workflow] = None


context = _Context()
