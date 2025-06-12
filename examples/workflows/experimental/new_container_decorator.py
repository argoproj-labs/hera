"""This example shows the use of the container decorator and special Input/Output classes."""

from typing_extensions import Annotated

from hera.shared import global_config
from hera.workflows import Input, Output, Parameter, Workflow

global_config.experimental_features["decorator_syntax"] = True


# We start by defining our Workflow
w = Workflow(generate_name="container-workflow-")


# This defines the template's inputs
class MyInput(Input):
    user: str = "Hera"


# This defines the template's outputs
class MyOutput(Output):
    container_greeting: Annotated[
        str,
        Parameter(
            name="container-greeting",
            value_from={"path": "/tmp/hello_world.txt"},
        ),
    ]


# We then use the decorators of the `Workflow` object
# to set the entrypoint and create a Container template
@w.set_entrypoint
@w.container(
    image="busybox",
    command=["sh", "-c"],
    args=["echo Hello {{inputs.parameters.user}} | tee /tmp/hello_world.txt"],
)
def basic_hello_world(my_input: MyInput) -> MyOutput: ...
