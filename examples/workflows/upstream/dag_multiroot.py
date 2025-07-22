from hera.workflows import DAG, Container, Task, Workflow
from hera.workflows.models import Arguments, Inputs, Parameter

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="dag-multiroot-",
    entrypoint="multiroot",
) as w:
    Container(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="message",
                )
            ],
        ),
        name="echo",
        command=["echo", "{{inputs.parameters.message}}"],
        image="alpine:3.7",
    )
    with DAG(
        name="multiroot",
    ) as invocator:
        Task(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="message",
                        value="A",
                    )
                ],
            ),
            name="A",
            template="echo",
        )
        Task(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="message",
                        value="B",
                    )
                ],
            ),
            name="B",
            template="echo",
        )
        Task(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="message",
                        value="C",
                    )
                ],
            ),
            name="C",
            template="echo",
            depends="A",
        )
        Task(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="message",
                        value="D",
                    )
                ],
            ),
            name="D",
            template="echo",
            depends="A && B",
        )
