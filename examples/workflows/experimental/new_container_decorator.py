from typing_extensions import Annotated

from hera.shared import global_config
from hera.workflows import Input, Output, Parameter, WorkflowTemplate

global_config.experimental_features["decorator_syntax"] = True


# We start by defining our Workflow Template
w = WorkflowTemplate(name="my-template")


# This defines the template's inputs
class MyInput(Input):
    user: str = "Hera"


class MyOutput(Output):
    container_greeting: Annotated[
        str,
        Parameter(
            name="container-greeting",
            value_from={"path": "/tmp/hello_world.txt"},
        ),
    ]


@w.set_entrypoint
@w.container(command=["sh", "-c"], args=["echo Hello {{inputs.parameters.user}} | tee /tmp/hello_world.txt"])
def basic_hello_world(my_input: MyInput) -> MyOutput: ...
