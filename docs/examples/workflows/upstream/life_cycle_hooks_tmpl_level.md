# Life Cycle Hooks Tmpl Level

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/life-cycle-hooks-tmpl-level.yaml).




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
        generate_name="lifecycle-hook-tmpl-level-",
        entrypoint="main",
    ) as w:
        echo = Container(
            name="echo",
            image="alpine:3.6",
            command=["sh", "-c"],
            args=['echo "it was heads"'],
        )
        http = HTTP(
            name="http",
            url="https://raw.githubusercontent.com/argoproj/argo-workflows/4e450e250168e6b4d51a126b784e90b11a0162bc/pkg/apis/workflow/v1alpha1/generated.swagger.json",
        )
        with Steps(name="main"):
            echo(
                name="step-1",
                hooks={
                    "running": m.LifecycleHook(expression='steps["step-1"].status == "Running"', template="http"),
                    "success": m.LifecycleHook(expression='steps["step-1"].status == "Succeeded"', template="http"),
                },
            )
            echo(
                name="step2",
                hooks={
                    "running": m.LifecycleHook(expression='steps.step2.status == "Running"', template="http"),
                    "success": m.LifecycleHook(expression='steps.step2.status == "Succeeded"', template="http"),
                },
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: lifecycle-hook-tmpl-level-
    spec:
      entrypoint: main
      templates:
      - name: echo
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
        - - hooks:
              running:
                expression: steps["step-1"].status == "Running"
                template: http
              success:
                expression: steps["step-1"].status == "Succeeded"
                template: http
            name: step-1
            template: echo
        - - hooks:
              running:
                expression: steps.step2.status == "Running"
                template: http
              success:
                expression: steps.step2.status == "Succeeded"
                template: http
            name: step2
            template: echo
    ```

