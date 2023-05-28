# Template On Exit

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/template-on-exit.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Workflow, Container, Steps

    with Workflow(generate_name="container-on-exit-", entrypoint="step-template") as w:
        exit_container = Container(
            name="exitContainer",
            image="docker/whalesay",
            command=["cowsay"],
            args=["goodbye world"],
        )
        whalesay = Container(
            name="whalesay",
            image="docker/whalesay",
            command=["cowsay"],
            args=["hello world"],
        )
        with Steps(name="step-template"):
            whalesay(name="stepA", on_exit=exit_container)
            whalesay(name="stepB", on_exit=exit_container)
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
          - cowsay
          image: docker/whalesay
        name: exitContainer
      - container:
          args:
          - hello world
          command:
          - cowsay
          image: docker/whalesay
        name: whalesay
      - name: step-template
        steps:
        - - name: stepA
            onExit: exitContainer
            template: whalesay
        - - name: stepB
            onExit: exitContainer
            template: whalesay
    ```

