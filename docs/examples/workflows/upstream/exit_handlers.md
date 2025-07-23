# Exit Handlers

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/exit-handlers.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="exit-handlers-",
        entrypoint="intentional-fail",
        on_exit="exit-handler",
    ) as w:
        Container(
            name="intentional-fail",
            args=["echo intentional failure; exit 1"],
            command=["sh", "-c"],
            image="alpine:latest",
        )
        with Steps(
            name="exit-handler",
        ) as invocator:
            with invocator.parallel():
                Step(
                    name="notify",
                    template="send-email",
                )
                Step(
                    name="celebrate",
                    template="celebrate",
                    when="{{workflow.status}} == Succeeded",
                )
                Step(
                    name="cry",
                    template="cry",
                    when="{{workflow.status}} != Succeeded",
                )
        Container(
            name="send-email",
            args=[
                "echo send e-mail: {{workflow.name}} {{workflow.status}} {{workflow.duration}}. Failed steps {{workflow.failures}}"
            ],
            command=["sh", "-c"],
            image="alpine:latest",
        )
        Container(
            name="celebrate",
            args=["echo hooray!"],
            command=["sh", "-c"],
            image="alpine:latest",
        )
        Container(
            name="cry",
            args=["echo boohoo!"],
            command=["sh", "-c"],
            image="alpine:latest",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: exit-handlers-
    spec:
      entrypoint: intentional-fail
      onExit: exit-handler
      templates:
      - name: intentional-fail
        container:
          image: alpine:latest
          args:
          - echo intentional failure; exit 1
          command:
          - sh
          - -c
      - name: exit-handler
        steps:
        - - name: notify
            template: send-email
          - name: celebrate
            template: celebrate
            when: '{{workflow.status}} == Succeeded'
          - name: cry
            template: cry
            when: '{{workflow.status}} != Succeeded'
      - name: send-email
        container:
          image: alpine:latest
          args:
          - 'echo send e-mail: {{workflow.name}} {{workflow.status}} {{workflow.duration}}.
            Failed steps {{workflow.failures}}'
          command:
          - sh
          - -c
      - name: celebrate
        container:
          image: alpine:latest
          args:
          - echo hooray!
          command:
          - sh
          - -c
      - name: cry
        container:
          image: alpine:latest
          args:
          - echo boohoo!
          command:
          - sh
          - -c
    ```

