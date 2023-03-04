import threading
from typing import List

from hera.workflows.v5._mixins import _SubNodeMixin
from hera.workflows.v5.exceptions import InvalidType
from hera.workflows.v5.protocol import Subbable


class _HeraContext(threading.local):
    def __init__(self) -> None:
        super().__init__()
        self._pieces: List[Subbable] = []

    def enter(self, p: Subbable) -> None:
        if not isinstance(p, Subbable):
            raise InvalidType()
        self._pieces.append(p)

    def exit(self) -> None:
        self._pieces.pop()

    def add_sub_node(self, node: _SubNodeMixin) -> None:
        if self._pieces:
            self._pieces[-1]._add_sub(node)


_context = _HeraContext()
