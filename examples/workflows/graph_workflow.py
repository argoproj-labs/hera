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
    with ContainerSet(name="main"):
        a = ContainerNode(name="a", image="argoproj/argosay:v2")
        b = ContainerNode(name="b", image="argoproj/argosay:v2")
        c = ContainerNode(name="c", image="argoproj/argosay:v2")
        d = ContainerNode(name="d", image="argoproj/argosay:v2")
        a >> [b, c] >> d
