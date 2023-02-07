"""Internal hera module to help transpile Python to expr.

This module primarily defines user-facing Constant class (aliased as `C` in the public module),
a Parentheses class to parenthesize expressions (aliased as `P` in the public module) and the Identifier
class which provides access to global and closure variables (aliased as `g` and `it` in the public module).
"""

from typing import Any, Dict, List, Optional, Union

# Primitives are the core primitive types available in expr
Primitives = Optional[Union[str, int, bool, float, range]]
Arrays = List[Any]
Maps = Dict[Primitives, Any]
# Constants is a type definition for all acceptable values for the `Constant` class.
Constants = Union[Primitives, Arrays, Maps]


class Node:
    """Node is the base class in our abstract syntax tree which helps Python to expr transpilation.

    It heavily uses the Python data model https://docs.python.org/3/reference/datamodel.html to
    provide a Python native way of constructing expr expressions.

    Once the final expression has been constructed, the python expression can be converted to the expr
    expression by calling str(expression) or repr(expression).
    """

    def __getattr__(self, name: str) -> "GetAttr":
        """Supports attribute access.

        This allows us to provide struct field access. Transpiles `var.<name>` to `var.<name>`.
        """
        return GetAttr(self, name)

    def __getitem__(self, name: str) -> "GetItem":
        """Supports index access.

        This allows us to provide index access. Transpiles `var[<name>]` to `var[<name>]`.
        """
        return GetItem(self, name)

    def __invert__(self):
        """Supports not unary operator.

        Transpiles `~var` to `!var`.
        """
        return UnaryOp(self, "!")

    def __neg__(self):
        """Supports not unary operator.

        Transpiles `-var` to `-var`.
        """
        return UnaryOp(self, "-")

    def __pos__(self):
        """Supports not unary operator.

        Transpiles `+var` to `+var`.
        """
        return UnaryOp(self, "+")

    def __format__(self, format_spec: str) -> str:
        """Supports easy output formatting to construct variable substitution expressions.

        Examples
        --------
        f"{g.input.parameters.value:$}" == "{{input.parameters.value}}"
        f"{g.workflow.parameters.config.jsonpath('$.a'):=}" == "{{=jsonpath(workflow.parameters.config, '$.a')}}"
        f"{g.input.parameters.value}" == "input.parameters.value"
        """
        # For more details around this see https://peps.python.org/pep-3101/
        if not format_spec:
            return repr(self)
        if format_spec == "$":
            return "{{" + repr(self) + "}}"
        if format_spec == "=":
            return "{{=" + repr(self) + "}}"
        raise Exception(f"Invalid format spec '{format_spec}'. Only allowed values are '$' and '='.")

    def length(self):
        """Supports length builtin.

        Transpiles `var.length()` to `len(var)`.
        """
        return Callable("len", self)

    def as_float(self):
        """Supports asFloat builtin.

        Transpiles `var.as_float()` to `asFloat(var)`.
        """
        return Callable("asFloat", self)

    def as_int(self):
        """Supports asInt builtin.

        Transpiles `var.as_int()` to `asInt(var)`.
        """
        return Callable("asInt", self)

    def check(self, truthy_value: 'Node', falsy_value: 'Node') -> 'Check':
        """Supports ternary operator.

        Transpiles `var.check(truthy_value, falsy_value)` to `var ? truthy_value : falsy_value`.
        """
        return Check(self, truthy_value, falsy_value)

    def get(self, name: str) -> "GetAttr":
        """Supports attribute access.

        This allows us to provide struct field access in case the field name conflicts with one of the Node methods.
        Transpiles `var.get(<name>)` to `var.<name>`.
        """
        return GetAttr(self, name)

    def jsonpath(self, path: str):
        """Supports jsonpath builtin.

        Transpiles `var.jsonpath(<path>)` to `jsonpath(var, <path>)`.
        """
        return Callable("jsonpath", self, Constant(str(path)))

    def string(self):
        """Supports string builtin.

        Transpiles `var.string()` to `string(var)`.
        """
        return Callable("string", self)

    def to_json(self):
        """Supports toJson builtin.

        Transpiles `var.to_json()` to `toJson(var)`.
        """
        return Callable("toJson", self)


# A list of binary operations supported by each node.
# Mapping what is available at
# https://github.com/antonmedv/expr/blob/34d2cbe7e43af1348d7010d951f1d7fe44a91500/checker/checker.go#L198
BINARY_OP_MAP = {
    # Refer to the Python data model to understand the dunder methods.
    # https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types
    # https://docs.python.org/3/reference/datamodel.html#object.__lt__
    # For all of these dunder methods, we transpile python statements like <node1> <python-operator> <node2>
    # to <node1> <expr-operator> <node2> statements. The dunder method names defined as keys
    # specify the way users can express the operation in python and the values
    # specify the operator in expr it will be transpiled to.
    "__add__": "+",
    "__and__": "&&",
    "__eq__": "==",
    "__ge__": ">=",
    "__gt__": ">",
    "__le__": "<=",
    "__lt__": "<",
    "__mod__": "%",
    "__mul__": "*",
    "__ne__": "!=",
    "__or__": "||",
    "__pow__": "**",
    "__sub__": "-",
    "__truediv__": "/",
    # These methods translate <node1>.<python-method>(<node2>) to <node1> <expr-operator> <node2>
    "contains": "contains",
    "ends_with": "endsWith",
    "in_": "in",
    "matches": "matches",
    "not_in": "not in",
    "starts_with": "startsWith",
}

# This defines a list of builtins that support a predicate along with a local
# iterator. See https://github.com/antonmedv/expr/blob/master/docs/Language-Definition.md#builtin-functions
# and https://github.com/antonmedv/expr/blob/master/docs/Language-Definition.md#closures for more details.
BUILTINS = (
    "all",
    "any",
    "count",
    "filter",
    "map",
    "none",
    "one",
)

# Here we dynamically set all the binary operators on the Node class
for method, op in BINARY_OP_MAP.items():

    # Note, we need a nested function here to properly bind
    # the op variable.
    # See https://eev.ee/blog/2011/04/24/gotcha-python-scoping-closures/#the-solution
    def operator(op: str):
        def func(self: Node, other: Node) -> "BinaryOp":
            if not isinstance(other, Node):
                other = Constant(other)
            return BinaryOp(self, other, op)

        return func

    setattr(Node, method, operator(op))

# Here we dynamically set all the builtin operators on the Node class
for builtin in BUILTINS:

    # Note, we need a nested function here to properly bind
    # the builtin variable.
    # See https://eev.ee/blog/2011/04/24/gotcha-python-scoping-closures/#the-solution
    def _builtin_func(builtin):
        def func(self: Node, operation: Node) -> "Builtin":
            return Builtin(builtin, self, operation)

        return func

    setattr(Node, builtin, _builtin_func(builtin))


def _constant_repr(obj):
    if obj is None:
        return 'nil'
    if obj is True:
        return 'true'
    if obj is False:
        return 'false'
    if isinstance(obj, range):
        return f"{obj.start}..{obj.stop - 1}"
    if isinstance(obj, list):
        return f'[{", ".join(map(_constant_repr, obj))}]'
    if isinstance(obj, dict):
        key_value_pairs = [f"{_constant_repr(key)}: {_constant_repr(value)}" for key, value in obj.items()]
        return f'{{{", ".join(key_value_pairs)}}}'
    return repr(obj)


class Constant(Node):
    """Supports transpiling inline python constants to expr expressions.

    Examples
    --------
    str(C(1)) == 1
    str(C(True)) == true
    str(C(None)) == nil
    str(C([1, 2, 3])) == [1, 2, 3]
    """

    def __init__(self, value: Constants):
        if isinstance(value, range):
            if value.step != 1:
                raise Exception("Only ranges with a step size of 1 are allowed")
        self.value = value

    def __repr__(self) -> str:
        # we need a custom repr function in order to recursively translate
        # True -> true, False -> false and None -> nil
        return _constant_repr(self.value)


class Identifier(Node):
    """Internal class used to define the `g` and `it` context variables."""

    def __init__(self, value: str = ""):
        self.value = value

    def __repr__(self) -> str:
        return self.value


class Parentheses(Node):
    """Supports transpiling groups of Python expressions so that they are parathesized properly in expr.

    Examples
    --------
    str(P(C(1) + C(2)) + 3) == (1 + 2) + 3
    """

    def __init__(self, value: Node):
        self.value = value

    def __repr__(self) -> str:
        return f"({self.value})"


class BinaryOp(Node):
    """Supports transpiling binary operators. See Node class for more information."""

    def __init__(self, value: Node, other_value: Node, operation: str):
        self.value = value
        self.other_value = other_value
        self.operation = operation

    def __repr__(self) -> str:
        return f"{self.value} {self.operation} {self.other_value}"


class UnaryOp(Node):
    """Supports transpiling unary operators. See Node class for more information."""

    def __init__(self, value: Node, operation: str):
        self.value = value
        self.operation = operation

    def __repr__(self) -> str:
        return f"{self.operation}{self.value}"


class Callable(Node):
    """Supports transpiling callables. See Node class for more information."""

    def __init__(self, function: str, *args: Any):
        self.function = function
        self.args = ", ".join(map(repr, map(lambda node: node if isinstance(node, Node) else Constant(node), args)))

    def __repr__(self) -> str:
        return f"{self.function}({self.args})"


class GetAttr(Node):
    """Supports transpiling attribute access. See Node class for more information."""

    def __init__(self, value: Node, attribute: str):
        self.value = value
        self.attribute = attribute

    def __repr__(self) -> str:
        return f"{self.value}.{self.attribute}" if str(self.value) else str(self.attribute)


class GetItem(Node):
    """Supports transpiling index access. See Node class for more information."""

    def __init__(self, value: Node, attribute: Union[str, int]):
        self.value = value
        if isinstance(attribute, slice):
            if attribute.step and attribute.step != 1:
                raise Exception("Only slices with a step size of 1 are allowed")
            start = attribute.start if attribute.start is not None else ''
            stop = attribute.stop if attribute.stop is not None else ''
            self.attribute = f"{start}:{stop}"
        else:
            self.attribute = repr(attribute)

    def __repr__(self) -> str:
        return f"{self.value}[{self.attribute}]"


class Builtin(Node):
    """Supports transpiling builtin expressions with predicates. See Node class for more information."""

    def __init__(self, operator: str, operand: Node, operation: Any):
        self.operator = operator
        self.operand = operand
        self.operation = operation if isinstance(operation, Node) else Constant(operation)

    def __repr__(self) -> str:
        return f"{self.operator}({self.operand}, {{{self.operation}}})"


class Check(Node):
    """Supports transpiling ternary operator. See Node class for more information."""

    def __init__(self, value: Node, truthy_value: Node, falsy_value: Node):
        self.value = value
        self.truthy_value = truthy_value
        self.falsy_value = falsy_value

    def __repr__(self) -> str:
        return f"{self.value} ? {self.truthy_value} : {self.falsy_value}"
