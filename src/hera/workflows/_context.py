import threading
from typing import List, TypeVar, Union

from hera.shared import BaseMixin
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
            raise InvalidType(type(p))
        self._pieces.append(p)

    def exit(self) -> None:
        self._pieces.pop()

    @property
    def active(self) -> bool:
        return bool(self._pieces)

    def add_sub_node(self, node: Union[SubNodeMixin, TTemplate]) -> None:
        if self._pieces:
            try:
                # here, we are trying to add a node to the last piece of context in the hopes that it is a subbable
                self._pieces[-1]._add_sub(node)
            except InvalidType:
                # if the above fails, it means the user invoked a decorated function e.g. `@script`. Hence,
                # the object needs to be added as a template to the piece of context at [-1]. This will be the case for
                # DAGs and Steps
                self._pieces[-1]._add_sub(node.template)  # type: ignore

            # when the above does not raise an exception, it means the user invoked a decorated function e.g. `@script`
            # inside a proper context. Here, we add the object to the overall workflow context, directly as a template,
            # in case it is not found (based on the name)
            if hasattr(node, "template") and node.template is not None and not isinstance(node.template, str):
                found = False
                for t in self._pieces[0].templates:  # type: ignore
                    if t.name == node.template.name:
                        found = True
                        break
                if not found:
                    self._pieces[0]._add_sub(node.template)


_context = _HeraContext()
