# Forever

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/forever.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Workflow

    with Workflow(
        name="forever",
        entrypoint="main",
    ) as w:
        Container(
            name="main",
            image="docker/whalesay:latest",
            command=["sh", "-c", "for I in $(seq 1 1000) ; do echo $I ; sleep 1s; done"],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      name: forever
    spec:
      entrypoint: main
      templates:
      - container:
          command:
          - sh
          - -c
          - for I in $(seq 1 1000) ; do echo $I ; sleep 1s; done
          image: docker/whalesay:latest
        name: main
    ```

