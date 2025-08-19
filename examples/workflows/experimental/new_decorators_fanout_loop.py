"""This example shows how to pass extra Step/Task kwargs when calling a function.

This lets you perform fanouts using `with_items`, set conditions using `when` and more.
"""

from hera.shared import global_config
from hera.workflows import Input, Workflow

global_config.experimental_features["decorator_syntax"] = True


w = Workflow(
    generate_name="fanout-workflow-",
    entrypoint="loop-example",
)


class PrintMessageInput(Input):
    message: str


@w.script()
def print_message(inputs: PrintMessageInput):
    print(inputs.message)


@w.steps()
def loop_example():
    print_message(
        PrintMessageInput(message="{{item}}"),
        name="print-message-loop-with-items",
        with_items=["hello world", "goodbye world"],
    )
