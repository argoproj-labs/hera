import threading
from typing import List, TypeVar, Union

from hera.shared._base_model import BaseMixin
from hera.workflows.exceptions import InvalidType
from hera.workflows.protocol import Subbable, TTemplate

TNode = TypeVar("TNode", bound="SubNodeMixin")


class SubNodeMixin(BaseMixin):
    """SubNodeMixin ensures that the class gets added to the Hera context on initialization."""

    def __hera_init__(self: TNode) -> TNode:
        _context.add_sub_node(self)
        return self


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

    def add_sub_node(self, node: Union[SubNodeMixin, TTemplate]) -> None:
        if self._pieces:
            self._pieces[-1]._add_sub(node)


_context = _HeraContext()
