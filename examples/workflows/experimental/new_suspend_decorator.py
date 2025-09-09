"""This example shows the use of the suspend decorator and special Input/Output classes."""

from typing_extensions import Annotated

from hera.shared import global_config
from hera.workflows import Input, Output, Parameter, Workflow
from hera.workflows.models import SuppliedValueFrom, ValueFrom

global_config.experimental_features["decorator_syntax"] = True


# We start by defining our Workflow
w = Workflow(generate_name="suspend-workflow-")


# This defines the template's inputs
class MyInput(Input):
    approve: Annotated[
        str,
        Parameter(
            description="Choose YES to continue workflow and deploy to production",
            enum=["YES", "NO"],
        ),
    ] = "NO"


class MyOutput(Output):
    approve: Annotated[
        str,
        Parameter(
            name="approve",
            value_from=ValueFrom(
                supplied=SuppliedValueFrom(),
            ),
        ),
    ]


# We then use the decorators of the `Workflow` object
# to set the entrypoint and create a Suspend template
@w.set_entrypoint
@w.suspend_template()
def basic_hello_world(my_input: MyInput) -> MyOutput: ...
