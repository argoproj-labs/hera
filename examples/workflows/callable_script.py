from typing import List

from pydantic import BaseModel

from hera.shared import global_config
from hera.workflows import Steps, Workflow, script

# Note, callable mode is only possible if the source code is available
# along with dependencies include hera in the image.
# Callable is a robust mode that allows you to run any python function
# and is compatible with pydantic. It automatically parses the input
# and serializes the output.
global_config.image = "my-image-with-python-source-code-and-dependencies"

# An optional pydantic input type
# hera can automatically de-serialize argo
# arguments into types denoted by your function's signature
# as long as they are de-serializable by pydantic
# This provides auto-magic input parsing with validation
# provided by pydantic.
class Input(BaseModel):
    a: int
    b: str = "foo"

# An optional pydantic output type
# hera can automatically serialize the output
# of your function into a json string
# as long as they are serializable by pydantic or json serializable
# This provides auto-magic output serialization with validation
# provided by pydantic.
class Output(BaseModel):
    output: List[Input]


@script(callable=True)
def my_function(input: Input) -> Output:
    return Output(output=[input])


# Note that the input type is a list of Input
# hera can also automatically de-serialize
# composite types like lists and dicts
@script(callable=True)
def another_function(inputs: List[Input]) -> Output:
    return Output(output=inputs)


# it also works with raw json strings
# but those must be explicitly marked as
# a string type
@script(callable=True)
def str_function(input: str) -> Output:
    # Example function to ensure we are not json parsing
    # string types before passing it to the function
    return Output(output=[Input.parse_raw(input)])


with Workflow(name="my-workflow") as w:
    with Steps(name="my-steps") as s:
        my_function(arguments={"input": Input(a=2, b="bar")})
        str_function(arguments={"input": Input(a=2, b="bar").json()})
        another_function(arguments={"inputs": [Input(a=2, b="bar"), Input(a=2, b="bar")]})
