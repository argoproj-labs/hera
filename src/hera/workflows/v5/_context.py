import threading
from typing import List, Union

from hera.workflows.v5._mixins import _SubNodeMixin
from hera.workflows.v5.exceptions import InvalidType
from hera.workflows.v5.protocol import Subbable, TTemplate, _DAGTaskMixin


class _HeraContext(threading.local):
    def __init__(self) -> None:
        super().__init__()
        self._pieces: List[Subbable] = []

    def enter(self, p: Subbable) -> None:
        if not isinstance(p, Subbable):
            raise InvalidType()
        self._pieces.append(p)

    def exit(self) -> None:
        if len(self._pieces) == 1:
            return  # only the workflow is in the context

        popped = self._pieces.pop()
        main = self._pieces[0]
        main._add_sub(popped)

    def add_sub_node(self, node: Union[_SubNodeMixin, TTemplate, _DAGTaskMixin]) -> None:
        self._pieces[-1]._add_sub(node)


_context = _HeraContext()
