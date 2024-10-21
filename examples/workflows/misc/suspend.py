from hera.workflows import Parameter, Suspend, Workflow

with Workflow(generate_name="suspend-", entrypoint="suspend-without-duration") as w:
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
