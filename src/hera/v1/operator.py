class OperatorValue:
    """OperatorValue is the value of an logic representation.

    This is used to represent the operator value.

    Attributes
    ----------
    value: str
        The value of an operator in str.
    """

    value: str

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class Operator2:
    """Operator is an logic representation.

    This can be used on conditional tasks workflow.

    Attributes
    ----------
    equals: str
        The logic '==' operator.
    greater: str
        The logic '>' operator.
    lower: str
        The logic '<' operator.
    greater_equals: str
        The logic >= operator.
    lower_equals: str
        The logic '<=' operator.
    not_equals: str
        The logic '!=' operator.
    """

    equals: str = '=='


class Operator:
    """Operator is an logic representation.

     This can be used on conditional tasks workflow.

    Attributes
     ----------
     value: str
         The value of an operator in str.
    """

    value: str

    equals: 'Operator' = None
    greater: 'Operator' = None
    lower: 'Operator' = None
    greater_equals: 'Operator' = None
    lower_equals: 'Operator' = None
    not_equals: 'Operator' = None

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


Operator.equals = Operator('==')
Operator.greater = Operator('>')
Operator.lower = Operator('<')
Operator.greater_equals = Operator('>=')
Operator.lower_equals = Operator('<=')
Operator.not_equals = Operator('!=')
