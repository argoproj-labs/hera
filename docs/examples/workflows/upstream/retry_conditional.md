# Retry Conditional

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/retry-conditional.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Script, Step, Steps, Workflow
    from hera.workflows.models import Arguments, Inputs, IntOrString, Parameter, RetryStrategy

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="retry-script-",
        entrypoint="main",
    ) as w:
        with Steps(
            name="main",
        ) as invocator:
            Step(
                name="safe-to-retry",
                template="safe-to-retry",
            )
            Step(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="safe-to-retry",
                            value="{{steps.safe-to-retry.outputs.result}}",
                        )
                    ],
                ),
                name="retry",
                template="retry-script",
            )
        Script(
            name="safe-to-retry",
            command=["python"],
            image="python:alpine3.6",
            source='print("true")\n',
        )
        Script(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="safe-to-retry",
                    )
                ],
            ),
            name="retry-script",
            retry_strategy=RetryStrategy(
                expression="""\
    asInt(lastRetry.exitCode) > 1 && \
    lastRetry.status != "Error" && \
    asInt(lastRetry.duration) < 120 && \
    ({{inputs.parameters.safe-to-retry}} == true || lastRetry.message matches 'imminent node shutdown|pod deleted')""",
                limit=IntOrString(
                    __root__="10",
                ),
            ),
            command=["python"],
            image="python:alpine3.6",
            source="import random;\nimport sys;\nexit_code = random.choice([1, 2]);\nsys.exit(exit_code)\n",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: retry-script-
    spec:
      entrypoint: main
      templates:
      - name: main
        steps:
        - - name: safe-to-retry
            template: safe-to-retry
        - - name: retry
            template: retry-script
            arguments:
              parameters:
              - name: safe-to-retry
                value: '{{steps.safe-to-retry.outputs.result}}'
      - name: safe-to-retry
        script:
          image: python:alpine3.6
          source: |
            print("true")
          command:
          - python
      - name: retry-script
        inputs:
          parameters:
          - name: safe-to-retry
        retryStrategy:
          expression: asInt(lastRetry.exitCode) > 1 && lastRetry.status != "Error" &&
            asInt(lastRetry.duration) < 120 && ({{inputs.parameters.safe-to-retry}} ==
            true || lastRetry.message matches 'imminent node shutdown|pod deleted')
          limit: '10'
        script:
          image: python:alpine3.6
          source: |
            import random;
            import sys;
            exit_code = random.choice([1, 2]);
            sys.exit(exit_code)
          command:
          - python
    ```

