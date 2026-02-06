# Loops Sequence

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/loops-sequence.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow
    from hera.workflows.models import Arguments, Inputs, IntOrString, Parameter, Sequence

    with Workflow(
        arguments=Arguments(
            parameters=[
                Parameter(
                    name="count",
                    value="3",
                )
            ],
        ),
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="loops-sequence-",
        entrypoint="loops-sequence",
    ) as w:
        with Steps(
            name="loops-sequence",
        ) as invocator:
            with invocator.parallel():
                Step(
                    arguments=Arguments(
                        parameters=[
                            Parameter(
                                name="msg",
                                value="{{item}}",
                            )
                        ],
                    ),
                    name="sequence-count",
                    template="echo",
                    with_sequence=Sequence(
                        count=IntOrString(
                            root="5",
                        ),
                    ),
                )
                Step(
                    arguments=Arguments(
                        parameters=[
                            Parameter(
                                name="msg",
                                value="{{item}}",
                            )
                        ],
                    ),
                    name="sequence-start-end",
                    template="echo",
                    with_sequence=Sequence(
                        end=IntOrString(
                            root="105",
                        ),
                        start=IntOrString(
                            root="100",
                        ),
                    ),
                )
                Step(
                    arguments=Arguments(
                        parameters=[
                            Parameter(
                                name="msg",
                                value="{{item}}",
                            )
                        ],
                    ),
                    name="sequence-param",
                    template="echo",
                    with_sequence=Sequence(
                        count=IntOrString(
                            root="{{workflow.parameters.count}}",
                        ),
                        start=IntOrString(
                            root="200",
                        ),
                    ),
                )
                Step(
                    arguments=Arguments(
                        parameters=[
                            Parameter(
                                name="msg",
                                value="{{item}}",
                            )
                        ],
                    ),
                    name="sequence-negative",
                    template="echo",
                    with_sequence=Sequence(
                        end=IntOrString(
                            root="0",
                        ),
                        start=IntOrString(
                            root="5",
                        ),
                    ),
                )
                Step(
                    arguments=Arguments(
                        parameters=[
                            Parameter(
                                name="msg",
                                value="{{item}}",
                            )
                        ],
                    ),
                    name="sequence-format",
                    template="echo",
                    with_sequence=Sequence(
                        count=IntOrString(
                            root="5",
                        ),
                        format="testuser%02X",
                    ),
                )
        Container(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="msg",
                    )
                ],
            ),
            name="echo",
            command=["echo", "{{inputs.parameters.msg}}"],
            image="alpine:latest",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: loops-sequence-
    spec:
      entrypoint: loops-sequence
      templates:
      - name: loops-sequence
        steps:
        - - name: sequence-count
            template: echo
            arguments:
              parameters:
              - name: msg
                value: '{{item}}'
            withSequence:
              count: '5'
          - name: sequence-start-end
            template: echo
            arguments:
              parameters:
              - name: msg
                value: '{{item}}'
            withSequence:
              end: '105'
              start: '100'
          - name: sequence-param
            template: echo
            arguments:
              parameters:
              - name: msg
                value: '{{item}}'
            withSequence:
              count: '{{workflow.parameters.count}}'
              start: '200'
          - name: sequence-negative
            template: echo
            arguments:
              parameters:
              - name: msg
                value: '{{item}}'
            withSequence:
              end: '0'
              start: '5'
          - name: sequence-format
            template: echo
            arguments:
              parameters:
              - name: msg
                value: '{{item}}'
            withSequence:
              count: '5'
              format: testuser%02X
      - name: echo
        container:
          image: alpine:latest
          command:
          - echo
          - '{{inputs.parameters.msg}}'
        inputs:
          parameters:
          - name: msg
      arguments:
        parameters:
        - name: count
          value: '3'
    ```

