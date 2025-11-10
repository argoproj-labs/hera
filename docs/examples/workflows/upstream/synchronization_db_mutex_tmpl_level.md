# Synchronization Db Mutex Tmpl Level

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/synchronization-db-mutex-tmpl-level.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow
    from hera.workflows.models import Arguments, Mutex, Parameter, Synchronization

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="synchronization-db-tmpl-level-mutex-",
        entrypoint="synchronization-db-tmpl-level-mutex-example",
    ) as w:
        with Steps(
            name="synchronization-db-tmpl-level-mutex-example",
        ) as invocator:
            with invocator.parallel():
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
                    name="synchronization-acquire-lock1",
                    template="acquire-lock-1",
                )
        Container(
            name="acquire-lock",
            synchronization=Synchronization(
                mutexes=[
                    Mutex(
                        name="welcome",
                        database=True,
                    )
                ],
            ),
            args=["sleep 20; echo acquired lock"],
            command=["sh", "-c"],
            image="alpine:latest",
        )
        Container(
            name="acquire-lock-1",
            synchronization=Synchronization(
                mutexes=[
                    Mutex(
                        name="test",
                        database=True,
                    )
                ],
            ),
            args=["sleep 50; echo acquired lock"],
            command=["sh", "-c"],
            image="alpine:latest",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: synchronization-db-tmpl-level-mutex-
    spec:
      entrypoint: synchronization-db-tmpl-level-mutex-example
      templates:
      - name: synchronization-db-tmpl-level-mutex-example
        steps:
        - - name: synchronization-acquire-lock
            template: acquire-lock
            withParam: '["1","2","3","4","5"]'
            arguments:
              parameters:
              - name: seconds
                value: '{{item}}'
          - name: synchronization-acquire-lock1
            template: acquire-lock-1
            withParam: '["1","2","3","4","5"]'
            arguments:
              parameters:
              - name: seconds
                value: '{{item}}'
      - name: acquire-lock
        container:
          image: alpine:latest
          args:
          - sleep 20; echo acquired lock
          command:
          - sh
          - -c
        synchronization:
          mutexes:
          - name: welcome
            database: true
      - name: acquire-lock-1
        container:
          image: alpine:latest
          args:
          - sleep 50; echo acquired lock
          command:
          - sh
          - -c
        synchronization:
          mutexes:
          - name: test
            database: true
    ```

