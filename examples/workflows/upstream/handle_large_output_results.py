from hera.workflows import Container, Step, Steps, Workflow
from hera.workflows.models import Arguments, Artifact, Inputs, IntOrString, Outputs, Parameter, Sequence, ValueFrom

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="handle-large-output-results-",
    entrypoint="handle-large-output-results",
) as w:
    with Steps(
        name="handle-large-output-results",
    ) as invocator:
        Step(
            name="get-items",
            template="get-items",
        )
        Step(
            arguments=Arguments(
                artifacts=[
                    Artifact(
                        from_="{{steps.get-items.outputs.artifacts.items}}",
                        name="items",
                    )
                ],
                parameters=[
                    Parameter(
                        name="index",
                        value="{{item}}",
                    )
                ],
            ),
            name="sequence-param",
            template="echo",
            with_sequence=Sequence(
                count=IntOrString(
                    __root__="{{steps.get-items.outputs.parameters.count}}",
                ),
            ),
        )
    Container(
        name="get-items",
        outputs=Outputs(
            artifacts=[
                Artifact(
                    name="items",
                    path="/tmp/items",
                )
            ],
            parameters=[
                Parameter(
                    name="count",
                    value_from=ValueFrom(
                        path="/tmp/count",
                    ),
                )
            ],
        ),
        args=['echo \'["a", "b", "c"]\' > /tmp/items && echo \'3\' > /tmp/count'],
        command=["/bin/sh", "-c"],
        image="alpine:latest",
    )
    Container(
        inputs=Inputs(
            artifacts=[
                Artifact(
                    name="items",
                    path="/tmp/items",
                )
            ],
            parameters=[
                Parameter(
                    name="index",
                )
            ],
        ),
        name="echo",
        args=["cat /tmp/items | jq '.[{{inputs.parameters.index}}]'"],
        command=["sh", "-c"],
        image="stedolan/jq:latest",
    )
