from hera.workflows import Container, Step, Steps, Workflow
from hera.workflows.models import Arguments, Inputs, Parameter

with Workflow(
    arguments=Arguments(
        parameters=[
            Parameter(
                name="seq-list",
                value='["a","b","c","d"]\n',
            )
        ],
    ),
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="parallelism-nested-workflow-",
    entrypoint="A",
) as w:
    with Steps(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="seq-list",
                )
            ],
        ),
        name="A",
        parallelism=1,
    ) as invocator:
        Step(
            with_param="{{inputs.parameters.seq-list}}",
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="seq-id",
                        value="{{item}}",
                    )
                ],
            ),
            name="seq-step",
            template="B",
        )
    with Steps(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="seq-id",
                )
            ],
        ),
        name="B",
    ) as invocator:
        Step(
            with_param="[1, 2]",
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="seq-id",
                        value="{{inputs.parameters.seq-id}}",
                    )
                ],
            ),
            name="jobs",
            template="one-job",
        )
    Container(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="seq-id",
                )
            ],
        ),
        name="one-job",
        args=["echo {{inputs.parameters.seq-id}}; sleep 30"],
        command=["/bin/sh", "-c"],
        image="alpine",
    )
