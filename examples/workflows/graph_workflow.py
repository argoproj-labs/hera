from hera.workflows.container_set import ContainerNode, ContainerSet
from hera.workflows.workflow import Workflow

with Workflow(
    generate_name="graph-",
    entrypoint="main",
    labels={"workflows.argoproj.io/test": "true"},
    annotations={
        "workflows.argoproj.io/description": "This workflow demonstrates running a graph of tasks within containers in a single pod.",
        "workflows.argoproj.io/version": ">= 3.1.0",
    },
) as w:
    ContainerSet(
        containers=[
            ContainerNode(name="a", image="argoproj/argosay:v2"),
            ContainerNode(name="b", image="argoproj/argosay:v2", dependencies=["a"]),
            ContainerNode(name="c", image="argoproj/argosay:v2", dependencies=["a"]),
            ContainerNode(name="d", image="argoproj/argosay:v2", dependencies=["b", "c"]),
        ],
    )
