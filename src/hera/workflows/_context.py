from contextvars import ContextVar
from typing import List, Optional, TypeVar, Union

from hera.shared import BaseMixin
from hera.workflows.exceptions import InvalidType
from hera.workflows.protocol import Subbable, TTemplate

TNode = TypeVar("TNode", bound="SubNodeMixin")

_pieces = ContextVar("_pieces", default=None)


class SubNodeMixin(BaseMixin):
    """SubNodeMixin ensures that the class gets added to the Hera context on initialization."""

    def __hera_init__(self: TNode) -> TNode:
        _context.add_sub_node(self)
        return self


class _HeraContext:
    """_HeraContext uses a ContextVar under the hood to store the context.

    Note: To avoid the ContextVar being shared, it must be lazily initialized to an empty list at runtime,
    and not at import time (Context is called at import time if we use the @script decorator for instance)
    """

    def enter(self, p: Subbable) -> None:
        if not isinstance(p, Subbable):
            raise InvalidType(type(p))
        if self.pieces is None:
            self.pieces = []
        self.pieces.append(p)

    def exit(self) -> None:
        if self.pieces:
            self.pieces.pop()

    @property
    def pieces(self) -> Optional[List[Subbable]]:
        """Get the context local variable for the pieces.

        The variable is None at import time to prevent shared state between contexts
        """
        return _pieces.get()

    @pieces.setter
    def pieces(self, value):
        _pieces.set(value)

    @property
    def active(self) -> bool:
        return bool(self.pieces)

    def add_sub_node(self, node: Union[SubNodeMixin, TTemplate]) -> None:
        pieces = self.pieces
        if not pieces:
            return

        try:
            # here, we are trying to add a node to the last piece of context in the hopes that it is a subbable
            pieces[-1]._add_sub(node)
        except InvalidType:
            # if the above fails, it means the user invoked a decorated function e.g. `@script`. Hence,
            # the object needs to be added as a template to the piece of context at [-1]. This will be the case for
            # DAGs and Steps
            pieces[-1]._add_sub(node.template)  # type: ignore

        # when the above does not raise an exception, it means the user invoked a decorated function e.g. `@script`
        # inside a proper context. Here, we add the object to the overall workflow context, directly as a template,
        # in case it is not found (based on the name)
        if hasattr(node, "template") and node.template is not None and not isinstance(node.template, str):
            found = False
            for t in pieces[0].templates:  # type: ignore
                if t.name == node.template.name:
                    found = True
                    break
            if not found:
                pieces[0]._add_sub(node.template)


_context = _HeraContext()
