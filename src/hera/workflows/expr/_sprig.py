"""Internal module to help transpile spring functions to expr.

See https://argoproj.github.io/argo-workflows/variables/#examples and
http://masterminds.github.io/sprig/ for more information.

Available publicly via the `sprig.<function>` variable.
"""

from typing import Any

from hera.expr._node import Callable


class _Method:
    def __init__(self, name: str):
        self.name = name

    def __call__(self, *args: Any, **_: Any) -> Any:
        return Callable(self.name, *args)


class Sprig:
    """Supports transpiling spring function calls."""

    def __getattr__(self, name: str) -> _Method:
        return _Method(f"sprig.{name}")
