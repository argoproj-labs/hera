# Nested Workflow

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/nested-workflow.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow
    from hera.workflows.models import Arguments, Artifact, Inputs, Outputs, Parameter, ValueFrom

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="nested-workflow-",
        entrypoint="nested-workflow-example",
    ) as w:
        with Steps(
            name="nested-workflow-example",
        ) as invocator:
            Step(
                name="generate",
                template="generate",
            )
            Step(
                arguments=Arguments(
                    artifacts=[
                        Artifact(
                            from_="{{steps.generate.outputs.artifacts.out-artifact}}",
                            name="nested-in-artifact",
                        )
                    ],
                    parameters=[
                        Parameter(
                            name="nested-in-parameter",
                            value="{{steps.generate.outputs.parameters.out-parameter}}",
                        )
                    ],
                ),
                name="nested-wf",
                template="nested-wf",
            )
            Step(
                arguments=Arguments(
                    artifacts=[
                        Artifact(
                            from_="{{steps.nested-wf.outputs.artifacts.nested-out-artifact}}",
                            name="in-artifact",
                        )
                    ],
                    parameters=[
                        Parameter(
                            name="in-parameter",
                            value="{{steps.nested-wf.outputs.parameters.nested-out-parameter}}",
                        )
                    ],
                ),
                name="consume",
                template="consume",
            )
        Container(
            name="generate",
            outputs=Outputs(
                artifacts=[
                    Artifact(
                        name="out-artifact",
                        path="/tmp/my-output-artifact.txt",
                    )
                ],
                parameters=[
                    Parameter(
                        name="out-parameter",
                        value_from=ValueFrom(
                            path="/tmp/my-output-parameter.txt",
                        ),
                    )
                ],
            ),
            args=[
                " echo hello world | tee /tmp/my-output-artifact.txt && echo 'my-output-parameter' > /tmp/my-output-parameter.txt "
            ],
            command=["sh", "-c"],
            image="busybox",
        )
        with Steps(
            inputs=Inputs(
                artifacts=[
                    Artifact(
                        name="nested-in-artifact",
                    )
                ],
                parameters=[
                    Parameter(
                        name="nested-in-parameter",
                    )
                ],
            ),
            name="nested-wf",
            outputs=Outputs(
                artifacts=[
                    Artifact(
                        from_="{{steps.generate.outputs.artifacts.out-artifact}}",
                        name="nested-out-artifact",
                    )
                ],
                parameters=[
                    Parameter(
                        name="nested-out-parameter",
                        value_from=ValueFrom(
                            parameter="{{steps.generate.outputs.parameters.out-parameter}}",
                        ),
                    )
                ],
            ),
        ) as invocator:
            with invocator.parallel():
                Step(
                    arguments=Arguments(
                        artifacts=[
                            Artifact(
                                from_="{{inputs.artifacts.nested-in-artifact}}",
                                name="in-artifact",
                            )
                        ],
                        parameters=[
                            Parameter(
                                name="in-parameter",
                                value="{{inputs.parameters.nested-in-parameter}}",
                            )
                        ],
                    ),
                    name="consume",
                    template="consume",
                )
                Step(
                    name="generate",
                    template="generate",
                )
        Container(
            inputs=Inputs(
                artifacts=[
                    Artifact(
                        name="in-artifact",
                        path="/tmp/art",
                    )
                ],
                parameters=[
                    Parameter(
                        name="in-parameter",
                    )
                ],
            ),
            name="consume",
            args=[
                " echo 'input parameter value: {{inputs.parameters.in-parameter}}' && echo 'input artifact contents:' && cat /tmp/art "
            ],
            command=["sh", "-c"],
            image="alpine:3.7",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: nested-workflow-
    spec:
      entrypoint: nested-workflow-example
      templates:
      - name: nested-workflow-example
        steps:
        - - name: generate
            template: generate
        - - name: nested-wf
            template: nested-wf
            arguments:
              artifacts:
              - name: nested-in-artifact
                from: '{{steps.generate.outputs.artifacts.out-artifact}}'
              parameters:
              - name: nested-in-parameter
                value: '{{steps.generate.outputs.parameters.out-parameter}}'
        - - name: consume
            template: consume
            arguments:
              artifacts:
              - name: in-artifact
                from: '{{steps.nested-wf.outputs.artifacts.nested-out-artifact}}'
              parameters:
              - name: in-parameter
                value: '{{steps.nested-wf.outputs.parameters.nested-out-parameter}}'
      - name: generate
        container:
          image: busybox
          args:
          - ' echo hello world | tee /tmp/my-output-artifact.txt && echo ''my-output-parameter''
            > /tmp/my-output-parameter.txt '
          command:
          - sh
          - -c
        outputs:
          artifacts:
          - name: out-artifact
            path: /tmp/my-output-artifact.txt
          parameters:
          - name: out-parameter
            valueFrom:
              path: /tmp/my-output-parameter.txt
      - name: nested-wf
        steps:
        - - name: consume
            template: consume
            arguments:
              artifacts:
              - name: in-artifact
                from: '{{inputs.artifacts.nested-in-artifact}}'
              parameters:
              - name: in-parameter
                value: '{{inputs.parameters.nested-in-parameter}}'
          - name: generate
            template: generate
        inputs:
          artifacts:
          - name: nested-in-artifact
          parameters:
          - name: nested-in-parameter
        outputs:
          artifacts:
          - name: nested-out-artifact
            from: '{{steps.generate.outputs.artifacts.out-artifact}}'
          parameters:
          - name: nested-out-parameter
            valueFrom:
              parameter: '{{steps.generate.outputs.parameters.out-parameter}}'
      - name: consume
        container:
          image: alpine:3.7
          args:
          - ' echo ''input parameter value: {{inputs.parameters.in-parameter}}'' && echo
            ''input artifact contents:'' && cat /tmp/art '
          command:
          - sh
          - -c
        inputs:
          artifacts:
          - name: in-artifact
            path: /tmp/art
          parameters:
          - name: in-parameter
    ```

