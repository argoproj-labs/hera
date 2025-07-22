from hera.workflows import DAG, Container, Task, Workflow
from hera.workflows.models import Arguments, Inputs, Parameter

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="exit-hanlder-dag-level-",
    entrypoint="main",
) as w:
    with DAG(
        name="main",
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
            on_exit="exit",
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
            on_exit="exit",
            template="echo",
            depends="A",
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
            on_exit="exit",
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
            on_exit="exit",
            template="echo",
            depends="B && C",
        )
    Container(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="message",
                )
            ],
        ),
        name="echo",
        args=["{{inputs.parameters.message}}"],
        command=["echo"],
        image="busybox",
    )
    Container(
        name="exit",
        args=["task cleanup"],
        command=["echo"],
        image="busybox",
    )
