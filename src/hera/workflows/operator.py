"""The operator module holds implementations of objects such as the operator enum."""

from enum import Enum


class Operator(Enum):
    """Operator is a representation of mathematical comparison symbols.

    This can be used on tasks that execute conditionally based on the output of another task.

    Notes:
        The task that outputs its result needs to do so using stdout. See `examples` for a sample workflow.
    """

    does_not_exist = "DoesNotExist"
    exists = "Exists"
    gt = "Gt"
    in_ = "In"
    lt = "Lt"
    not_in = "NotIn"

    equals = "=="
    greater = ">"
    less = "<"
    greater_equal = ">="
    less_equal = "<="
    not_equal = "!="
    or_ = "||"
    and_ = "&&"
    starts_with = "=~"

    def __str__(self) -> str:
        """Assembles the `value` representation of the enum and returns it as a string."""
        return str(self.value)


__all__ = ["Operator"]
