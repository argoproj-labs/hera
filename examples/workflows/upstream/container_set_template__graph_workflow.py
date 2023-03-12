from hera.workflows.container_set import ContainerNode, ContainerSet
from hera.workflows.workflow import Workflow

with Workflow(
    generate_name="graph-",
    entrypoint="main",
) as w:
    with ContainerSet(name="main"):
        a = ContainerNode(name="a", image="argoproj/argosay:v2")
        b = ContainerNode(name="b", image="argoproj/argosay:v2")
        c = ContainerNode(name="c", image="argoproj/argosay:v2")
        d = ContainerNode(name="d", image="argoproj/argosay:v2")
        a >> [b, c] >> d
