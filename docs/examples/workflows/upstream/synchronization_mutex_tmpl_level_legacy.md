# Synchronization Mutex Tmpl Level Legacy

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/synchronization-mutex-tmpl-level-legacy.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Container,
        Steps,
        Workflow,
        models as m,
    )

    with Workflow(
        generate_name="synchronization-tmpl-level-mutex-",
        entrypoint="synchronization-tmpl-level-mutex-example",
    ) as w:
        acquire_lock = Container(
            name="acquire-lock",
            image="alpine:latest",
            command=["sh", "-c"],
            args=["sleep 20; echo acquired lock"],
            synchronization=m.Synchronization(mutex=m.Mutex(name="welcome")),
        )
        acquire_lock_1 = Container(
            name="acquire-lock-1",
            image="alpine:latest",
            command=["sh", "-c"],
            args=["sleep 50; echo acquired lock"],
            synchronization=m.Synchronization(mutex=m.Mutex(name="test")),
        )
        with Steps(name="synchronization-tmpl-level-mutex-example") as s:
            with s.parallel():
                acquire_lock(
                    name="synchronization-acquire-lock",
                    arguments={"seconds": "{{item}}"},
                    with_param='["1","2","3","4","5"]',
                )

                acquire_lock_1(
                    name="synchronization-acquire-lock1",
                    arguments={"seconds": "{{item}}"},
                    with_param='["1","2","3","4","5"]',
                )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: synchronization-tmpl-level-mutex-
    spec:
      entrypoint: synchronization-tmpl-level-mutex-example
      templates:
      - name: acquire-lock
        container:
          image: alpine:latest
          args:
          - sleep 20; echo acquired lock
          command:
          - sh
          - -c
        synchronization:
          mutex:
            name: welcome
      - name: acquire-lock-1
        container:
          image: alpine:latest
          args:
          - sleep 50; echo acquired lock
          command:
          - sh
          - -c
        synchronization:
          mutex:
            name: test
      - name: synchronization-tmpl-level-mutex-example
        steps:
        - - arguments:
              parameters:
              - name: seconds
                value: '{{item}}'
            name: synchronization-acquire-lock
            template: acquire-lock
            withParam: '["1","2","3","4","5"]'
          - arguments:
              parameters:
              - name: seconds
                value: '{{item}}'
            name: synchronization-acquire-lock1
            template: acquire-lock-1
            withParam: '["1","2","3","4","5"]'
    ```

