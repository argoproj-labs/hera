# Handle Large Output Results

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/handle-large-output-results.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow
    from hera.workflows.models import Arguments, Artifact, Inputs, IntOrString, Outputs, Parameter, Sequence, ValueFrom

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="handle-large-output-results-",
        entrypoint="handle-large-output-results",
    ) as w:
        with Steps(
            name="handle-large-output-results",
        ) as invocator:
            Step(
                name="get-items",
                template="get-items",
            )
            Step(
                arguments=Arguments(
                    artifacts=[
                        Artifact(
                            from_="{{steps.get-items.outputs.artifacts.items}}",
                            name="items",
                        )
                    ],
                    parameters=[
                        Parameter(
                            name="index",
                            value="{{item}}",
                        )
                    ],
                ),
                name="sequence-param",
                template="echo",
                with_sequence=Sequence(
                    count=IntOrString(
                        root="{{steps.get-items.outputs.parameters.count}}",
                    ),
                ),
            )
        Container(
            name="get-items",
            outputs=Outputs(
                artifacts=[
                    Artifact(
                        name="items",
                        path="/tmp/items",
                    )
                ],
                parameters=[
                    Parameter(
                        name="count",
                        value_from=ValueFrom(
                            path="/tmp/count",
                        ),
                    )
                ],
            ),
            args=['echo \'["a", "b", "c"]\' > /tmp/items && echo \'3\' > /tmp/count'],
            command=["/bin/sh", "-c"],
            image="alpine:latest",
        )
        Container(
            inputs=Inputs(
                artifacts=[
                    Artifact(
                        name="items",
                        path="/tmp/items",
                    )
                ],
                parameters=[
                    Parameter(
                        name="index",
                    )
                ],
            ),
            name="echo",
            args=["cat /tmp/items | jq '.[{{inputs.parameters.index}}]'"],
            command=["sh", "-c"],
            image="stedolan/jq:latest",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: handle-large-output-results-
    spec:
      entrypoint: handle-large-output-results
      templates:
      - name: handle-large-output-results
        steps:
        - - name: get-items
            template: get-items
        - - name: sequence-param
            template: echo
            arguments:
              artifacts:
              - name: items
                from: '{{steps.get-items.outputs.artifacts.items}}'
              parameters:
              - name: index
                value: '{{item}}'
            withSequence:
              count: '{{steps.get-items.outputs.parameters.count}}'
      - name: get-items
        container:
          image: alpine:latest
          args:
          - echo '["a", "b", "c"]' > /tmp/items && echo '3' > /tmp/count
          command:
          - /bin/sh
          - -c
        outputs:
          artifacts:
          - name: items
            path: /tmp/items
          parameters:
          - name: count
            valueFrom:
              path: /tmp/count
      - name: echo
        container:
          image: stedolan/jq:latest
          args:
          - cat /tmp/items | jq '.[{{inputs.parameters.index}}]'
          command:
          - sh
          - -c
        inputs:
          artifacts:
          - name: items
            path: /tmp/items
          parameters:
          - name: index
    ```

