"""This example shows a simple "hello world" script using the new decorators.

It uses a single input argument, which is passed through the `Workflow`. It also
uses a plain `Output` - by setting the `result` value, it will be printed to stdout
and be available to subsequent tasks (if it were in a DAG).
"""

from hera.shared import global_config
from hera.workflows import Input, Output, Workflow

global_config.experimental_features["decorator_syntax"] = True

w = Workflow(name="hello-world", arguments={"user": "me"})


class MyInput(Input):
    user: str


@w.set_entrypoint
@w.script()
def hello_world(my_input: MyInput) -> Output:
    output = Output()
    output.result = f"Hello Hera User: {my_input.user}!"
    return output
