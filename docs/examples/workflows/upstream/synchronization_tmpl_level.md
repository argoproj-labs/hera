# Synchronization Tmpl Level

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/synchronization-tmpl-level.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow
    from hera.workflows.models import Arguments, ConfigMapKeySelector, Parameter, SemaphoreRef, Synchronization

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="synchronization-tmpl-level-",
        entrypoint="synchronization-tmpl-level-example",
    ) as w:
        with Steps(
            name="synchronization-tmpl-level-example",
        ) as invocator:
            Step(
                with_param='["1","2","3","4","5"]',
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="seconds",
                            value="{{item}}",
                        )
                    ],
                ),
                name="synchronization-acquire-lock",
                template="acquire-lock",
            )
        Container(
            name="acquire-lock",
            synchronization=Synchronization(
                semaphores=[
                    SemaphoreRef(
                        config_map_key_ref=ConfigMapKeySelector(
                            key="template",
                            name="my-config",
                        ),
                    )
                ],
            ),
            args=["sleep 10; echo acquired lock"],
            command=["sh", "-c"],
            image="alpine:latest",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: synchronization-tmpl-level-
    spec:
      entrypoint: synchronization-tmpl-level-example
      templates:
      - name: synchronization-tmpl-level-example
        steps:
        - - name: synchronization-acquire-lock
            template: acquire-lock
            withParam: '["1","2","3","4","5"]'
            arguments:
              parameters:
              - name: seconds
                value: '{{item}}'
      - name: acquire-lock
        container:
          image: alpine:latest
          args:
          - sleep 10; echo acquired lock
          command:
          - sh
          - -c
        synchronization:
          semaphores:
          - configMapKeyRef:
              name: my-config
              key: template
    ```

