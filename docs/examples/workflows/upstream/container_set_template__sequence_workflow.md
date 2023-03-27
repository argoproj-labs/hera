# Container Set Template  Sequence Workflow

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/container-set-template/sequence-workflow.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import ContainerNode, ContainerSet, Workflow

    with Workflow(
        generate_name="sequence-",
        entrypoint="main",
    ) as w:
        with ContainerSet(name="main"):
            (
                ContainerNode(name="a", image="argoproj/argosay:v2")
                >> ContainerNode(name="b", image="argoproj/argosay:v2")
                >> ContainerNode(name="c", image="argoproj/argosay:v2")
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: sequence-
    spec:
      entrypoint: main
      templates:
      - containerSet:
          containers:
          - image: argoproj/argosay:v2
            name: a
          - dependencies:
            - a
            image: argoproj/argosay:v2
            name: b
          - dependencies:
            - b
            image: argoproj/argosay:v2
            name: c
        name: main
    ```

