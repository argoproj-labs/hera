# Recursive For Loop

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/recursive-for-loop.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Script, Step, Steps, Workflow
    from hera.workflows.models import Arguments, Inputs, Parameter

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="recursive-loop-",
        entrypoint="plan",
    ) as w:
        with Steps(
            name="plan",
        ) as invocator:
            Step(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="counter",
                            value="0",
                        ),
                        Parameter(
                            name="limit",
                            value="10",
                        ),
                    ],
                ),
                name="recurse",
                template="loop",
            )
        with Steps(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="counter",
                    ),
                    Parameter(
                        name="limit",
                    ),
                ],
            ),
            name="loop",
        ) as invocator:
            Step(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="counter",
                            value="{{inputs.parameters.counter}}",
                        )
                    ],
                ),
                name="iterate-counter",
                template="counter-iteration",
            )
            Step(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="counter",
                            value="{{steps.iterate-counter.outputs.result}}",
                        ),
                        Parameter(
                            name="limit",
                            value="{{inputs.parameters.limit}}",
                        ),
                    ],
                ),
                name="continue",
                template="loop",
                when="{{steps.iterate-counter.outputs.result}} < {{inputs.parameters.limit}}",
            )
        Script(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="counter",
                    )
                ],
            ),
            name="counter-iteration",
            command=["python"],
            image="python:alpine3.6",
            source="print({{inputs.parameters.counter}} + 1)\n",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: recursive-loop-
    spec:
      entrypoint: plan
      templates:
      - name: plan
        steps:
        - - name: recurse
            template: loop
            arguments:
              parameters:
              - name: counter
                value: '0'
              - name: limit
                value: '10'
      - name: loop
        steps:
        - - name: iterate-counter
            template: counter-iteration
            arguments:
              parameters:
              - name: counter
                value: '{{inputs.parameters.counter}}'
        - - name: continue
            template: loop
            when: '{{steps.iterate-counter.outputs.result}} < {{inputs.parameters.limit}}'
            arguments:
              parameters:
              - name: counter
                value: '{{steps.iterate-counter.outputs.result}}'
              - name: limit
                value: '{{inputs.parameters.limit}}'
        inputs:
          parameters:
          - name: counter
          - name: limit
      - name: counter-iteration
        inputs:
          parameters:
          - name: counter
        script:
          image: python:alpine3.6
          source: |
            print({{inputs.parameters.counter}} + 1)
          command:
          - python
    ```

