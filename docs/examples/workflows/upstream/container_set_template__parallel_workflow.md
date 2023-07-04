# Container Set Template  Parallel Workflow

> Note: This example is a replication of an Argo Workflow example in Hera. 




=== "Hera"

    ```python linenums="1"
    from hera.workflows import ContainerNode, ContainerSet, Workflow

    with Workflow(
        generate_name="parallel-",
        entrypoint="main",
    ) as w:
        with ContainerSet(name="main"):
            ContainerNode(name="a", image="argoproj/argosay:v2")
            ContainerNode(name="b", image="argoproj/argosay:v2")
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: parallel-
    spec:
      entrypoint: main
      templates:
      - containerSet:
          containers:
          - image: argoproj/argosay:v2
            name: a
          - image: argoproj/argosay:v2
            name: b
        name: main
    ```

