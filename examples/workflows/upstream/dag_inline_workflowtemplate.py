from hera.workflows import Container, DAG, Task, WorkflowTemplate


container = Container(image="argoproj/argosay:v2")

with WorkflowTemplate(
    name="dag-inline",
    entrypoint="main",
    annotations={
        "workflows.argoproj.io/description": (
            "This example demonstrates running a DAG with inline templates."
        ),
        "workflows.argoproj.io/version": ">= 3.2.0",
    },
) as w:
    with DAG(name="main"):
        Task(name="a", inline=container)
