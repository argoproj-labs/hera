# Exit Handler Dag Level

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/exit-handler-dag-level.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, Task, Workflow
    from hera.workflows.models import Arguments, Inputs, Parameter

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="exit-hanlder-dag-level-",
        entrypoint="main",
    ) as w:
        with DAG(
            name="main",
        ) as invocator:
            Task(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="message",
                            value="A",
                        )
                    ],
                ),
                name="A",
                on_exit="exit",
                template="echo",
            )
            Task(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="message",
                            value="B",
                        )
                    ],
                ),
                name="B",
                on_exit="exit",
                template="echo",
                depends="A",
            )
            Task(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="message",
                            value="C",
                        )
                    ],
                ),
                name="C",
                on_exit="exit",
                template="echo",
                depends="A",
            )
            Task(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="message",
                            value="D",
                        )
                    ],
                ),
                name="D",
                on_exit="exit",
                template="echo",
                depends="B && C",
            )
        Container(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="message",
                    )
                ],
            ),
            name="echo",
            args=["{{inputs.parameters.message}}"],
            command=["echo"],
            image="busybox",
        )
        Container(
            name="exit",
            args=["task cleanup"],
            command=["echo"],
            image="busybox",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: exit-hanlder-dag-level-
    spec:
      entrypoint: main
      templates:
      - name: main
        dag:
          tasks:
          - name: A
            onExit: exit
            template: echo
            arguments:
              parameters:
              - name: message
                value: A
          - name: B
            depends: A
            onExit: exit
            template: echo
            arguments:
              parameters:
              - name: message
                value: B
          - name: C
            depends: A
            onExit: exit
            template: echo
            arguments:
              parameters:
              - name: message
                value: C
          - name: D
            depends: B && C
            onExit: exit
            template: echo
            arguments:
              parameters:
              - name: message
                value: D
      - name: echo
        container:
          image: busybox
          args:
          - '{{inputs.parameters.message}}'
          command:
          - echo
        inputs:
          parameters:
          - name: message
      - name: exit
        container:
          image: busybox
          args:
          - task cleanup
          command:
          - echo
    ```

