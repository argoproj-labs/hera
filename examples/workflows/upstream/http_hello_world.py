from hera.workflows import HTTP, Step, Steps, Workflow
from hera.workflows.models import Arguments, ContinueOn, Inputs, Parameter

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    annotations={
        "workflows.argoproj.io/description": "Http template will demostrate http template functionality\n",
        "workflows.argoproj.io/version": ">= 3.2.0",
    },
    generate_name="http-template-",
    labels={"workflows.argoproj.io/test": "true"},
    entrypoint="main",
) as w:
    with Steps(
        name="main",
    ) as invocator:
        with invocator.parallel():
            Step(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="url",
                            value="https://raw.githubusercontent.com/argoproj/argo-workflows/4e450e250168e6b4d51a126b784e90b11a0162bc/pkg/apis/workflow/v1alpha1/generated.swagger.json",
                        )
                    ],
                ),
                name="good",
                template="http",
            )
            Step(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="url",
                            value="https://raw.githubusercontent.com/argoproj/argo-workflows/thisisnotahash/pkg/apis/workflow/v1alpha1/generated.swagger.json",
                        )
                    ],
                ),
                name="bad",
                continue_on=ContinueOn(
                    failed=True,
                ),
                template="http",
            )
    HTTP(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="url",
                )
            ],
        ),
        name="http",
        url="{{inputs.parameters.url}}",
    )
