# Parallelism Nested Workflow

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/parallelism-nested-workflow.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow
    from hera.workflows.models import Arguments, Inputs, Parameter

    with Workflow(
        arguments=Arguments(
            parameters=[
                Parameter(
                    name="seq-list",
                    value='["a","b","c","d"]\n',
                )
            ],
        ),
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="parallelism-nested-workflow-",
        entrypoint="A",
    ) as w:
        with Steps(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="seq-list",
                    )
                ],
            ),
            name="A",
            parallelism=1,
        ) as invocator:
            Step(
                with_param="{{inputs.parameters.seq-list}}",
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="seq-id",
                            value="{{item}}",
                        )
                    ],
                ),
                name="seq-step",
                template="B",
            )
        with Steps(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="seq-id",
                    )
                ],
            ),
            name="B",
        ) as invocator:
            Step(
                with_param="[1, 2]",
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="seq-id",
                            value="{{inputs.parameters.seq-id}}",
                        )
                    ],
                ),
                name="jobs",
                template="one-job",
            )
        Container(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="seq-id",
                    )
                ],
            ),
            name="one-job",
            args=["echo {{inputs.parameters.seq-id}}; sleep 30"],
            command=["/bin/sh", "-c"],
            image="alpine",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: parallelism-nested-workflow-
    spec:
      entrypoint: A
      templates:
      - name: A
        parallelism: 1
        steps:
        - - name: seq-step
            template: B
            withParam: '{{inputs.parameters.seq-list}}'
            arguments:
              parameters:
              - name: seq-id
                value: '{{item}}'
        inputs:
          parameters:
          - name: seq-list
      - name: B
        steps:
        - - name: jobs
            template: one-job
            withParam: '[1, 2]'
            arguments:
              parameters:
              - name: seq-id
                value: '{{inputs.parameters.seq-id}}'
        inputs:
          parameters:
          - name: seq-id
      - name: one-job
        container:
          image: alpine
          args:
          - echo {{inputs.parameters.seq-id}}; sleep 30
          command:
          - /bin/sh
          - -c
        inputs:
          parameters:
          - name: seq-id
      arguments:
        parameters:
        - name: seq-list
          value: |
            ["a","b","c","d"]
    ```

