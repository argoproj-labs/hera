# Template On Exit

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/template-on-exit.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Steps, Workflow

    with Workflow(generate_name="container-on-exit-", entrypoint="step-template") as w:
        exit_container = Container(
            name="exitContainer",
            image="busybox",
            command=["echo"],
            args=["goodbye world"],
        )
        hello_world = Container(
            name="hello-world",
            image="busybox",
            command=["echo"],
            args=["hello world"],
        )
        with Steps(name="step-template"):
            hello_world(name="stepA", on_exit=exit_container)
            hello_world(name="stepB", on_exit=exit_container)
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: container-on-exit-
    spec:
      entrypoint: step-template
      templates:
      - container:
          args:
          - goodbye world
          command:
          - echo
          image: busybox
        name: exitContainer
      - container:
          args:
          - hello world
          command:
          - echo
          image: busybox
        name: hello-world
      - name: step-template
        steps:
        - - name: stepA
            onExit: exitContainer
            template: hello-world
        - - name: stepB
            onExit: exitContainer
            template: hello-world
    ```

