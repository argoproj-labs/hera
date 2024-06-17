"""Module that manages Hera's use of contexts.

This module provides the functionality necessary to support the implementation backing elements such as `with`
clauses for workflows and DAGs.
"""

from contextvars import ContextVar
from typing import List, Optional, TypeVar, Union

from hera.shared import BaseMixin
from hera.workflows.exceptions import InvalidType, TemplateNameConflict
from hera.workflows.protocol import Subbable, TTemplate

TNode = TypeVar("TNode", bound="SubNodeMixin")

_pieces = ContextVar("_pieces", default=None)
_declaring = ContextVar("_declaring", default=False)


class SubNodeMixin(BaseMixin):
    """SubNodeMixin ensures that the class gets added to the Hera context on initialization.

    The mixin implements the core Hera `__hera_init__`, which is invoked post Hera object initialization. Anything
    that inherits from this mixin has the capacity to manage a context via either being added to a context (like being
    added to a Workflow/DAG) or managing a context itself (like holding Container, Script, etc).
    """

    def __hera_init__(self: TNode) -> TNode:
        """The Hera init that is invoked post object initialization."""
        _context.add_sub_node(self)
        return self


class _HeraContext:
    """_HeraContext uses a ContextVar under the hood to store the context.

    Notes:
    -----
    To avoid the ContextVar being shared, it must be lazily initialized to an empty list at runtime,
    and not at import time (Context is called at import time if we use the @script decorator for instance).
    """

    def enter(self, p: Subbable) -> None:
        """Adds the given 'subbable' piece to the context of the current parent object."""
        if not isinstance(p, Subbable):
            raise InvalidType(type(p))
        if self.pieces is None:
            self.pieces = []
        self.pieces.append(p)

    def exit(self) -> None:
        """Pops the latest 'subbable' piece from the context."""
        if self.pieces:
            self.pieces.pop()

    @property
    def pieces(self) -> Optional[List[Subbable]]:
        """Get the context local variable for the pieces.

        The variable is None at import time to prevent shared state between contexts.
        """
        return _pieces.get()

    @pieces.setter
    def pieces(self, value) -> None:
        """Sets the given values as the pieces of the context."""
        _pieces.set(value)

    @property
    def declaring(self) -> bool:
        return _declaring.get()

    @declaring.setter
    def declaring(self, value: bool) -> None:
        _declaring.set(value)

    @property
    def active(self) -> bool:
        """Tells whether there's an active context."""
        return bool(self.pieces)

    def add_sub_node(self, node: Union[SubNodeMixin, TTemplate]) -> None:
        """Adds the given node to the active context."""
        pieces = self.pieces
        if not pieces:
            return

        # When the user invokes a decorated function e.g. `@script inside a sub-context (dag/steps),
        # we also add the step/task's template to the overall workflow context, if it is not already added.
        from hera.workflows._mixins import TemplateInvocatorSubNodeMixin

        if (
            isinstance(node, TemplateInvocatorSubNodeMixin)
            and node.template is not None
            and not isinstance(node.template, str)
        ):
            from hera.workflows.workflow import Workflow

            if not isinstance(pieces[0], Workflow):
                raise SyntaxError("Not under a Workflow context")

            found = False
            for t in pieces[0].templates:
                if t.name == node.template.name:
                    if t != node.template:
                        raise TemplateNameConflict(f"Found multiple templates with the same name: {t.name}")
                    found = True
                    break
            if not found:
                pieces[0]._add_sub(node.template)

        pieces[-1]._add_sub(node)


_context = _HeraContext()
