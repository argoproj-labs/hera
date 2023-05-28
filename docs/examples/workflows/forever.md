# Forever






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
            command=["sh", "-c"],
            args=["for I in $(seq 1 1000) ; do echo $I ; sleep 1s; done"],
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
          args:
          - for I in $(seq 1 1000) ; do echo $I ; sleep 1s; done
          command:
          - sh
          - -c
          image: docker/whalesay:latest
        name: main
    ```

