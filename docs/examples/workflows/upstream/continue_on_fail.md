# Continue On Fail

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/continue-on-fail.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Container,
        Steps,
        Workflow,
        models as m,
    )

    with Workflow(
        generate_name="continue-on-fail-",
        entrypoint="workflow-ignore",
        parallelism=1,
    ) as w:
        whalesay = Container(
            name="whalesay",
            image="docker/whalesay:latest",
            command=["cowsay"],
            args=["hello world"],
        )
        intentional_fail = Container(
            name="intentional-fail",
            image="alpine:latest",
            command=["sh", "-c"],
            args=["echo intentional failure; exit 1"],
        )
        with Steps(name="workflow-ignore") as steps:
            whalesay(name="A")
            with steps.parallel():
                whalesay(name="B")
                intentional_fail(name="C", continue_on=m.ContinueOn(failed=True))
            whalesay(name="D")
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: continue-on-fail-
    spec:
      entrypoint: workflow-ignore
      parallelism: 1
      templates:
      - container:
          args:
          - hello world
          command:
          - cowsay
          image: docker/whalesay:latest
        name: whalesay
      - container:
          args:
          - echo intentional failure; exit 1
          command:
          - sh
          - -c
          image: alpine:latest
        name: intentional-fail
      - name: workflow-ignore
        steps:
        - - name: A
            template: whalesay
        - - name: B
            template: whalesay
          - continueOn:
              failed: true
            name: C
            template: intentional-fail
        - - name: D
            template: whalesay
    ```

