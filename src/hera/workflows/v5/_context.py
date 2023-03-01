import threading
from typing import List, Union

from hera.workflows.v5.container import Container
from hera.workflows.v5.workflow import Workflow

AcceptedCtx = Union[Workflow]
AcceptedTemplates = Union[Container]


class _HeraContext(threading.local):

    def __init__(self) -> None:
        super().__init__()
        self._pieces: List[AcceptedCtx] = []

    def enter(self, p: AcceptedCtx) -> None:
        self._pieces.append(p)

    def exit(self) -> None:
        self._pieces.pop()

    def add_template(self, t: AcceptedTemplates) -> None:
        if self._pieces[-1].templates is None:
            self._pieces[-1].templates = [t._build_template()]
        else:
            self._pieces[-1].templates.append(t._build_template())


_context = _HeraContext()
