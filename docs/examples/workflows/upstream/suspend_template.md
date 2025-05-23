# Suspend Template

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/suspend-template.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Steps, Suspend, Workflow

    with Workflow(
        generate_name="suspend-template-",
        entrypoint="suspend",
    ) as w:
        hello_world = Container(name="hello-world", image="busybox", command=["echo"], args=["hello world"])

        approve = Suspend(name="approve")
        delay = Suspend(name="delay", duration=20)

        with Steps(name="suspend"):
            hello_world(name="build")
            approve()
            delay()
            hello_world(name="release")
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: suspend-template-
    spec:
      entrypoint: suspend
      templates:
      - name: hello-world
        container:
          image: busybox
          args:
          - hello world
          command:
          - echo
      - name: approve
        suspend: {}
      - name: delay
        suspend:
          duration: '20'
      - name: suspend
        steps:
        - - name: build
            template: hello-world
        - - name: approve
            template: approve
        - - name: delay
            template: delay
        - - name: release
            template: hello-world
    ```

