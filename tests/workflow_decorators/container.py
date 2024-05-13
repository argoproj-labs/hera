from typing import Optional

from typing_extensions import Annotated

from hera.shared import global_config
from hera.workflows import Container, Input, Output, Parameter, WorkflowTemplate

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_pydantic_io"] = True
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
def basic_hello_world(my_input: MyInput) -> Output: ...


@w.container(command=["sh", "-c"])
def advanced_hello_world(my_input: MyInput, template: Optional[Container] = None) -> MyOutput:
    # A 'MyOutput' object can be used to "mock" the output when running locally and allow us to
    # inject outputs based on inputs.
    output: MyOutput = MyOutput(container_greeting=f"Hello {my_input.user}")

    # template is a special variable that allows you to reference the template itself and modify
    # its attributes. This is especially useful when trying to reference input params in args.
    # The hio.path function will be able to inspect the annotation of the given variable
    # to return the correct Argo template syntax substitution.
    if template:
        template.args = [f"echo Hello {my_input.user} > tee /tmp/hello_world.txt"]
    # template.args = [f"echo Hello {my_input.user} > {hio.path(output.container_greeting)}"]
    return output
