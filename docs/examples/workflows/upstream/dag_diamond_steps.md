# Dag Diamond Steps

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-diamond-steps.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, Step, Steps, Task, Workflow
    from hera.workflows.models import Arguments, Inputs, Item, Parameter

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="dag-diamond-steps-",
        entrypoint="diamond",
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
        with Steps(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="message",
                    )
                ],
            ),
            name="echo-thrice",
        ) as invocator:
            Step(
                with_items=[
                    Item(
                        __root__=1,
                    ),
                    Item(
                        __root__=2,
                    ),
                    Item(
                        __root__=3,
                    ),
                ],
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="message",
                            value="{{inputs.parameters.message}}{{item}}",
                        )
                    ],
                ),
                name="echo",
                template="echo",
            )
        with DAG(
            name="diamond",
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
                template="echo-thrice",
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
                template="echo-thrice",
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
                template="echo-thrice",
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
                template="echo-thrice",
                depends="B && C",
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dag-diamond-steps-
    spec:
      entrypoint: diamond
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
      - name: echo-thrice
        steps:
        - - name: echo
            template: echo
            withItems:
            - 1
            - 2
            - 3
            arguments:
              parameters:
              - name: message
                value: '{{inputs.parameters.message}}{{item}}'
        inputs:
          parameters:
          - name: message
      - name: diamond
        dag:
          tasks:
          - name: A
            template: echo-thrice
            arguments:
              parameters:
              - name: message
                value: A
          - name: B
            depends: A
            template: echo-thrice
            arguments:
              parameters:
              - name: message
                value: B
          - name: C
            depends: A
            template: echo-thrice
            arguments:
              parameters:
              - name: message
                value: C
          - name: D
            depends: B && C
            template: echo-thrice
            arguments:
              parameters:
              - name: message
                value: D
    ```

