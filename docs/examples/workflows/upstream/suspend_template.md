# Suspend Template

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/suspend-template.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Steps, Suspend, Workflow

    with Workflow(
        generate_name="suspend-template-",
        entrypoint="suspend",
    ) as w:
        whalesay = Container(name="whalesay", image="docker/whalesay", command=["cowsay"], args=["hello world"])

        approve = Suspend(name="approve")
        delay = Suspend(name="delay", duration=20)

        with Steps(name="suspend"):
            whalesay(name="build")
            approve()
            delay()
            whalesay(name="release")
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
      - container:
          args:
          - hello world
          command:
          - cowsay
          image: docker/whalesay
        name: whalesay
      - name: approve
        suspend: {}
      - name: delay
        suspend:
          duration: '20'
      - name: suspend
        steps:
        - - name: build
            template: whalesay
        - - name: approve
            template: approve
        - - name: delay
            template: delay
        - - name: release
            template: whalesay
    ```

