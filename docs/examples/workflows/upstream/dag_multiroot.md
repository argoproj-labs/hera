# Dag Multiroot

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-multiroot.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, Task, Workflow
    from hera.workflows.models import Arguments, Inputs, Parameter

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="dag-multiroot-",
        entrypoint="multiroot",
    ) as w:
        Container(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="message",
                    )
                ],
            ),
            name="echo",
            command=["echo", "{{inputs.parameters.message}}"],
            image="alpine:3.7",
        )
        with DAG(
            name="multiroot",
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
                template="echo",
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
                template="echo",
                depends="A && B",
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dag-multiroot-
    spec:
      entrypoint: multiroot
      templates:
      - name: echo
        container:
          image: alpine:3.7
          command:
          - echo
          - '{{inputs.parameters.message}}'
        inputs:
          parameters:
          - name: message
      - name: multiroot
        dag:
          tasks:
          - name: A
            template: echo
            arguments:
              parameters:
              - name: message
                value: A
          - name: B
            template: echo
            arguments:
              parameters:
              - name: message
                value: B
          - name: C
            depends: A
            template: echo
            arguments:
              parameters:
              - name: message
                value: C
          - name: D
            depends: A && B
            template: echo
            arguments:
              parameters:
              - name: message
                value: D
    ```

