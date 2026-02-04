from hera.workflows import Parameter, Step, Steps, Suspend, Workflow

with Workflow(
    generate_name="suspend-input-duration-",
    entrypoint="suspend",
) as w:
    intermediate_params = Suspend(
        name="suspend-with-intermediate-param",
        intermediate_parameters=[Parameter(name="duration")],
    )

    configurable_suspend_template = Suspend(
        name="input-duration-suspend",
        inputs=[Parameter(name="duration", default="10")],
        duration="{{inputs.parameters.duration}}",
    )

    with Steps(name="suspend"):
        get_value_step = intermediate_params(name="get-value-step")

        Step(
            name="custom-delay-step",
            template=configurable_suspend_template,
            arguments={"duration": get_value_step.get_parameter("duration")},
        )
