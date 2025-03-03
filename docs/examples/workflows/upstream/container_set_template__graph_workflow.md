# Container Set Template  Graph Workflow

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/container-set-template/graph-workflow.yaml).




=== "Hera"

    ```python linenums="1"
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
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: graph-
    spec:
      entrypoint: main
      templates:
      - name: main
        containerSet:
          containers:
          - name: a
            image: argoproj/argosay:v2
          - name: b
            image: argoproj/argosay:v2
            dependencies:
            - a
          - name: c
            image: argoproj/argosay:v2
            dependencies:
            - a
          - name: d
            image: argoproj/argosay:v2
            dependencies:
            - b
            - c
    ```

