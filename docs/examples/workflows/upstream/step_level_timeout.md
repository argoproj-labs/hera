# Step Level Timeout

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/step-level-timeout.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow
    from hera.workflows.models import Arguments, ContinueOn, Inputs, Parameter

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="steps-tmpl-timeout-",
        entrypoint="sleep-sleep",
    ) as w:
        with Steps(
            name="sleep-sleep",
        ) as invocator:
            with invocator.parallel():
                Step(
                    arguments=Arguments(
                        parameters=[
                            Parameter(
                                name="timeout",
                                value="10s",
                            )
                        ],
                    ),
                    name="sleep1",
                    continue_on=ContinueOn(
                        error=True,
                    ),
                    template="sleep",
                )
                Step(
                    arguments=Arguments(
                        parameters=[
                            Parameter(
                                name="timeout",
                                value="10s",
                            )
                        ],
                    ),
                    name="sleep2",
                    continue_on=ContinueOn(
                        failed=True,
                    ),
                    template="sleep",
                )
        Container(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="timeout",
                    )
                ],
            ),
            name="sleep",
            timeout="{{inputs.parameters.timeout}}",
            args=["sleep 30s"],
            command=["sh", "-c"],
            image="alpine:latest",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: steps-tmpl-timeout-
    spec:
      entrypoint: sleep-sleep
      templates:
      - name: sleep-sleep
        steps:
        - - name: sleep1
            template: sleep
            arguments:
              parameters:
              - name: timeout
                value: 10s
            continueOn:
              error: true
          - name: sleep2
            template: sleep
            arguments:
              parameters:
              - name: timeout
                value: 10s
            continueOn:
              failed: true
      - name: sleep
        timeout: '{{inputs.parameters.timeout}}'
        container:
          image: alpine:latest
          args:
          - sleep 30s
          command:
          - sh
          - -c
        inputs:
          parameters:
          - name: timeout
    ```

