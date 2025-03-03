# Container Set Template  Parallel Workflow

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/container-set-template/parallel-workflow.yaml).




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
      - name: main
        containerSet:
          containers:
          - name: a
            image: argoproj/argosay:v2
          - name: b
            image: argoproj/argosay:v2
    ```

