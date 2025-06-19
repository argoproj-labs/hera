"""The `hera.workflows.template_set` module provides the TemplateSet class.

The `TemplateSet` class lets you create a collection of templates unattached to a Workflow.

Warning:
    This class is only for use with experimental Workflow decorators. [Read the guide here](../../../user-guides/decorators.md).
"""

from typing import Any, List, Union

from hera.workflows._meta_mixins import TemplateDecoratorFuncsMixin
from hera.workflows.exceptions import InvalidType
from hera.workflows.models import (
    Template as _ModelTemplate,
)
from hera.workflows.protocol import Templatable


class TemplateSet(
    TemplateDecoratorFuncsMixin,
):
    """The TemplateSet class can be used to arrange templates across modules in a package."""

    templates: List[Union[_ModelTemplate, Templatable]] = []

    def _add_sub(self, node: Any):
        """Adds the given node (expected to satisfy the `Templatable` protocol) to the context."""
        if not isinstance(node, (Templatable, _ModelTemplate)):
            raise InvalidType(type(node))
        self.templates.append(node)


__all__ = ["TemplateSet"]
