from hera.workflows.parameter import Parameter
from hera.workflows.suspend import Suspend
from hera.workflows.workflow import Workflow

with Workflow(generate_name="suspend-") as w:
    Suspend(name="suspend-without-duration")
    Suspend(name="suspend-with-duration", duration=30)
    Suspend(
        name="suspend-with-intermediate-param-enum",
        intermediate_parameters=[Parameter(name="approve", enum=["YES", "NO"], default="NO")],
    )
    Suspend(
        name="suspend-with-intermediate-param",
        intermediate_parameters=[Parameter(name="approve")],
    )
