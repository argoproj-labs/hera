from hera.expr import g
from hera.workflows import HTTP, Parameter, Workflow

with Workflow(generate_name="http-") as w:
    HTTP(
        name="http",
        inputs=[Parameter(name="url")],
        timeout_seconds=20,
        url=f"{g.inputs.parameters.url:$}",
        method="GET",
        headers=[{"name": "x-header-name", "value": "test-value"}],
        success_condition=str(g.response.body.contains("google")),  # type: ignore
        body="test body",
    )
