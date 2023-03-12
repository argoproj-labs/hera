from hera.workflows import ContainerNode, ContainerSet, Workflow

with Workflow(
    generate_name="parallel-",
    entrypoint="main",
) as w:
    with ContainerSet(name="main"):
        ContainerNode(name="a", image="argoproj/argosay:v2")
        ContainerNode(name="b", image="argoproj/argosay:v2")
