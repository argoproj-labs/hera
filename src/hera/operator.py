from enum import Enum


class Operator(str, Enum):
    """Operator is a representation of mathematical comparison symbols.

     This can be used on tasks that execute conditionally based on the output of another task.

    Notes
    -----
    The task that outputs its result needs to do so using stdout. See `examples` for a sample workflow.
    """

    Equals = "=="
    Greater = ">"
    Less = "<"
    GreaterEqual = ">="
    LessEqual = "<="
    NotEqual = "!="
    Or = "||"
    And = "&&"
    StartsWith = "=~"

    def __str__(self):
        return str(self.value)
