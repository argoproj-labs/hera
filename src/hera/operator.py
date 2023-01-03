from enum import Enum

from hera.models import Operator as GeneratedOperator


class Operator(GeneratedOperator):
    """Operator is a representation of mathematical comparison symbols.

     This can be used on tasks that execute conditionally based on the output of another task.

    Notes
    -----
    The task that outputs its result needs to do so using stdout. See `examples` for a sample workflow.
    """

    equals = "=="
    greater = ">"
    less = "<"
    greater_equal = ">="
    less_equal = "<="
    not_equal = "!="
    or_ = "||"
    and_ = "&&"
    starts_with = "=~"

    def __str__(self):
        return str(self.value)
