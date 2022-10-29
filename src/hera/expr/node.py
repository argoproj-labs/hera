from typing import Any, Dict, List, Optional, Union

Primitives = Optional[Union[str, int, bool, float]]
Arrays = List[Any]
Maps = Dict[Primitives, Any]
Constant = Union[Primitives, Arrays, Maps]

# Mapping what is available at
# https://github.com/antonmedv/expr/blob/34d2cbe7e43af1348d7010d951f1d7fe44a91500/checker/checker.go#L198
_BinaryOpMap = {
    "__add__": "+",
    "__sub__": "-",
    "__mul__": "*",
    "__truediv__": "/",
    "__pow__": "**",
    "__mod__": "%",
    "__and__": "and",
    "__or__": "or",
    "__ge__": ">=",
    "__gt__": ">",
    "__le__": "<=",
    "__lt__": "<",
    "__eq__": "==",
    "__ne__": "==",
}


class _Node:
    def length(self):
        return _Len(self)

    def __getattr__(self, name: str) -> "_GetAttr":
        return _GetAttr(self, name)

    def __getitem__(self, name: str) -> "_GetItem":
        return _GetItem(self, name)


for method, op in _BinaryOpMap.items():

    def operator(op: str):
        def func(self: _Node, other: _Node) -> "_BinaryOp":
            if not isinstance(self, _Node):
                self = C(self)
            if not isinstance(other, _Node):
                other = C(other)
            return _BinaryOp(self, other, op)

        return func

    setattr(_Node, method, operator(op))


class C(_Node):
    def __init__(self, value: Constant):
        self.value = value

    def __repr__(self) -> str:
        return repr(self.value)


class I(_Node):  # noqa: E742
    def __init__(self, value: str):
        self.value = value

    def __repr__(self) -> str:
        return self.value


class B(_Node):
    def __init__(self, value: _Node):
        self.value = value

    def __repr__(self) -> str:
        return f"({self.value})"


class _BinaryOp(_Node):
    def __init__(self, value: _Node, other_value: _Node, operation: str):
        self.value = value
        self.other_value = other_value
        self.operation = operation

    def __repr__(self) -> str:
        return f"{self.value} {self.operation} {self.other_value}"


class _Len(_Node):
    def __init__(self, value: _Node):
        self.value = value

    def __repr__(self) -> str:
        return f"len({self.value})"


class _GetAttr(_Node):
    def __init__(self, value: _Node, attribute: str):
        self.value = value
        self.attribute = attribute

    def __repr__(self) -> str:
        return f"{self.value}.{self.attribute}"


class _GetItem(_Node):
    def __init__(self, value: _Node, attribute: Union[str, int]):
        self.value = value
        self.attribute = repr(attribute)

    def __repr__(self) -> str:
        return f"{self.value}[{self.attribute}]"
