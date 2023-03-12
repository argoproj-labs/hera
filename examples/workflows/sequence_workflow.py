from hera.workflows.container_set import ContainerNode, ContainerSet
from hera.workflows.workflow import Workflow

with Workflow(
    generate_name="sequence-",
    entrypoint="main",
    labels={"workflows.argoproj.io/test": "true"},
    annotations={
        "workflows.argoproj.io/description": "This workflow demonstrates running a sequence of containers within a single pod.",
        "workflows.argoproj.io/version": ">= 3.1.0",
    },
) as w:
    with ContainerSet(name="main"):
        (
            ContainerNode(name="a", image="argoproj/argosay:v2")
            >> ContainerNode(name="b", image="argoproj/argosay:v2")
            >> ContainerNode(name="c", image="argoproj/argosay:v2")
        )
