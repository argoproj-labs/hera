from typing import Any, Protocol


class Buildable(Protocol):
    def build(self) -> Any:
        raise NotImplementedError
