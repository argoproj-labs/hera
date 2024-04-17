from hera.workflows import Step, Steps, Suspend, Workflow
from hera.workflows.models import Inputs, Parameter, SuspendTemplate, Template

with Workflow(
    generate_name="suspend-input-duration-",
    entrypoint="suspend",
) as w:
    intermediate_params = Suspend(
        name="suspend-with-intermediate-param",
        intermediate_parameters=[Parameter(name="duration")],
    )

    configurable_suspend_template = Template(
        name="input-duration-suspend",
        suspend=SuspendTemplate(duration="{{inputs.parameters.duration}}"),
        inputs=Inputs(parameters=[Parameter(name="duration", default="10")]),
    )

    with Steps(name="suspend"):
        intermediate_params(name="get-value-step")

        Step(
            name="custom-delay-step",
            template=configurable_suspend_template,
            arguments={"duration": "{{steps.get-value-step.outputs.parameters.duration}}"},
        )
