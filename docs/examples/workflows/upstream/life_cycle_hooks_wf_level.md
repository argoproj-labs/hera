# Life Cycle Hooks Wf Level

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/life-cycle-hooks-wf-level.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        HTTP,
        Container,
        Steps,
        Workflow,
        models as m,
    )

    with Workflow(
        generate_name="lifecycle-hook-",
        entrypoint="main",
        hooks={
            "exit": m.LifecycleHook(template="http"),
            "running": m.LifecycleHook(expression='workflow.status == "Running"', template="http"),
        },
    ) as w:
        heads = Container(
            name="heads",
            image="alpine:3.6",
            command=["sh", "-c"],
            args=['echo "it was heads"'],
        )
        http = HTTP(
            name="http",
            url="https://raw.githubusercontent.com/argoproj/argo-workflows/4e450e250168e6b4d51a126b784e90b11a0162bc/pkg/apis/workflow/v1alpha1/generated.swagger.json",
        )
        with Steps(name="main"):
            heads(name="step1")
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: lifecycle-hook-
    spec:
      entrypoint: main
      templates:
      - name: heads
        container:
          image: alpine:3.6
          args:
          - echo "it was heads"
          command:
          - sh
          - -c
      - name: http
        http:
          url: https://raw.githubusercontent.com/argoproj/argo-workflows/4e450e250168e6b4d51a126b784e90b11a0162bc/pkg/apis/workflow/v1alpha1/generated.swagger.json
      - name: main
        steps:
        - - name: step1
            template: heads
      hooks:
        exit:
          template: http
        running:
          expression: workflow.status == "Running"
          template: http
    ```

