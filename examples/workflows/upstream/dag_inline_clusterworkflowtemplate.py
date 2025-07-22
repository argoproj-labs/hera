from hera.workflows import DAG, ClusterWorkflowTemplate, Container, Task

with ClusterWorkflowTemplate(
    api_version="argoproj.io/v1alpha1",
    kind="ClusterWorkflowTemplate",
    annotations={
        "workflows.argoproj.io/description": "This examples demonstrates running a DAG with inline templates.\n",
        "workflows.argoproj.io/version": ">= 3.2.0",
    },
    name="dag-inline",
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
