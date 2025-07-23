# Hello World

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/hello-world.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Workflow

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        annotations={"workflows.argoproj.io/description": "This is a simple hello world example.\n"},
        generate_name="hello-world-",
        labels={"workflows.argoproj.io/archive-strategy": "false"},
        entrypoint="hello-world",
    ) as w:
        Container(
            name="hello-world",
            args=["hello world"],
            command=["echo"],
            image="busybox",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: hello-world-
      annotations:
        workflows.argoproj.io/description: |
          This is a simple hello world example.
      labels:
        workflows.argoproj.io/archive-strategy: 'false'
    spec:
      entrypoint: hello-world
      templates:
      - name: hello-world
        container:
          image: busybox
          args:
          - hello world
          command:
          - echo
    ```

