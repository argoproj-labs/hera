# Continue On Fail

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/continue-on-fail.yaml).




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
        hello_world = Container(
            name="hello-world",
            image="busybox",
            command=["echo"],
            args=["hello world"],
        )
        intentional_fail = Container(
            name="intentional-fail",
            image="alpine:latest",
            command=["sh", "-c"],
            args=["echo intentional failure; exit 1"],
        )
        with Steps(name="workflow-ignore") as steps:
            hello_world(name="A")
            with steps.parallel():
                hello_world(name="B")
                intentional_fail(name="C", continue_on=m.ContinueOn(failed=True))
            hello_world(name="D")
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
      - name: hello-world
        container:
          image: busybox
          args:
          - hello world
          command:
          - echo
      - name: intentional-fail
        container:
          image: alpine:latest
          args:
          - echo intentional failure; exit 1
          command:
          - sh
          - -c
      - name: workflow-ignore
        steps:
        - - name: A
            template: hello-world
        - - name: B
            template: hello-world
          - continueOn:
              failed: true
            name: C
            template: intentional-fail
        - - name: D
            template: hello-world
    ```

