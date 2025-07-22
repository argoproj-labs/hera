from hera.workflows import DAG, Container, Task, Workflow

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    annotations={
        "workflows.argoproj.io/description": "This example demonstrates running a DAG with inline templates.\n",
        "workflows.argoproj.io/version": ">= 3.2.0",
    },
    generate_name="dag-inline-",
    labels={"workflows.argoproj.io/test": "true"},
    entrypoint="main",
) as w:
    with DAG(
        name="main",
    ) as invocator:
        Task(
            name="a",
            inline=Container(
                image="argoproj/argosay:v2",
            ),
        )
