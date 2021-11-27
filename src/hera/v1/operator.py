from enum import Enum


class Operator(Enum):
    """Operator is an logic representation.

     This can be used on conditional tasks workflow.

    Attributes
     ----------
     value: str
         The value of an operator in str.
    """

    equals = '=='
    greater = '>'
    lower = '<'
    greater_equal = '>='
    lower_equal = '<='
    not_equal = '!='
