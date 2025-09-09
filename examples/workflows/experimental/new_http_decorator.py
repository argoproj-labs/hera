"""This example shows the use of the http decorator and special Input/Output classes."""

from typing_extensions import Annotated

from hera.expr import g
from hera.shared import global_config
from hera.workflows import Input, Output, Parameter, Workflow
from hera.workflows.models import SuppliedValueFrom, ValueFrom

global_config.experimental_features["decorator_syntax"] = True


# We start by defining our Workflow
w = Workflow(generate_name="http-workflow-")


# This defines the template's inputs
class MyInput(Input):
    url: str = "https://example.com"


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
# to set the entrypoint and create a HTTP template
@w.set_entrypoint
@w.http_template(
    timeout_seconds=20,
    url=f"{g.inputs.parameters.url:$}",
    method="GET",
    headers=[{"name": "x-header-name", "value": "test-value"}],
    success_condition=str(g.response.body.contains("google")),  # type: ignore
    body="test body",
)
def basic_hello_world(my_input: MyInput) -> MyOutput: ...
