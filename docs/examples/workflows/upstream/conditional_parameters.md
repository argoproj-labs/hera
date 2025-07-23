# Conditional Parameters

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/conditional-parameters.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Script, Step, Steps, Workflow
    from hera.workflows.models import Outputs, Parameter, ValueFrom

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        annotations={
            "workflows.argoproj.io/description": "Conditional parameters provide a way to choose the output parameters based on expression.\n\nIn this example the step template has two steps which will run conditionally on `when`.\n\nBased on that condition, one of step will not be executed. The step template's output parameter will be\nset from the executed step's output.\n",
            "workflows.argoproj.io/version": ">= 3.1.0",
        },
        generate_name="conditional-parameter-",
        labels={"workflows.argoproj.io/test": "true"},
        entrypoint="main",
    ) as w:
        with Steps(
            name="main",
            outputs=Outputs(
                parameters=[
                    Parameter(
                        name="stepresult",
                        value_from=ValueFrom(
                            expression="steps['flip-coin'].outputs.result == 'heads' ? steps.heads.outputs.result : steps.tails.outputs.result",
                        ),
                    )
                ],
            ),
        ) as invocator:
            Step(
                name="flip-coin",
                template="flip-coin",
            )
            with invocator.parallel():
                Step(
                    name="heads",
                    template="heads",
                    when="{{steps.flip-coin.outputs.result}} == heads",
                )
                Step(
                    name="tails",
                    template="tails",
                    when="{{steps.flip-coin.outputs.result}} == tails",
                )
        Script(
            name="flip-coin",
            command=["python"],
            image="python:alpine3.6",
            source='import random\nprint("heads" if random.randint(0,1) == 0 else "tails")\n',
        )
        Script(
            name="heads",
            command=["python"],
            image="python:alpine3.6",
            source='print("heads")\n',
        )
        Script(
            name="tails",
            command=["python"],
            image="python:alpine3.6",
            source='print("tails")\n',
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: conditional-parameter-
      annotations:
        workflows.argoproj.io/description: |
          Conditional parameters provide a way to choose the output parameters based on expression.

          In this example the step template has two steps which will run conditionally on `when`.

          Based on that condition, one of step will not be executed. The step template's output parameter will be
          set from the executed step's output.
        workflows.argoproj.io/version: '>= 3.1.0'
      labels:
        workflows.argoproj.io/test: 'true'
    spec:
      entrypoint: main
      templates:
      - name: main
        steps:
        - - name: flip-coin
            template: flip-coin
        - - name: heads
            template: heads
            when: '{{steps.flip-coin.outputs.result}} == heads'
          - name: tails
            template: tails
            when: '{{steps.flip-coin.outputs.result}} == tails'
        outputs:
          parameters:
          - name: stepresult
            valueFrom:
              expression: 'steps[''flip-coin''].outputs.result == ''heads'' ? steps.heads.outputs.result
                : steps.tails.outputs.result'
      - name: flip-coin
        script:
          image: python:alpine3.6
          source: |
            import random
            print("heads" if random.randint(0,1) == 0 else "tails")
          command:
          - python
      - name: heads
        script:
          image: python:alpine3.6
          source: |
            print("heads")
          command:
          - python
      - name: tails
        script:
          image: python:alpine3.6
          source: |
            print("tails")
          command:
          - python
    ```

