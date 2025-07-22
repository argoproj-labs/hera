# Dag Conditional Artifacts

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-conditional-artifacts.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Script, Task, Workflow
    from hera.workflows.models import Artifact, Outputs

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        annotations={
            "workflows.argoproj.io/description": "Conditional artifacts provides a way to choose the output artifacts based on an expression.\n\nIn this example the DAG template has two tasks which will run conditionall using `when`.\n\nBased on the condition one of steps may not execute. The step template output's artifact will be set to the\nexecuted step's output artifacts.\n",
            "workflows.argoproj.io/version": ">= 3.1.0",
        },
        generate_name="dag-conditional-artifacts-",
        labels={"workflows.argoproj.io/test": "true"},
        entrypoint="main",
    ) as w:
        with DAG(
            name="main",
            outputs=Outputs(
                artifacts=[
                    Artifact(
                        from_expression="tasks['flip-coin'].outputs.result == 'heads' ? tasks.heads.outputs.artifacts.result : tasks.tails.outputs.artifacts.result",
                        name="result",
                    )
                ],
            ),
        ) as invocator:
            Task(
                name="flip-coin",
                template="flip-coin",
            )
            Task(
                name="heads",
                template="heads",
                when="{{tasks.flip-coin.outputs.result}} == heads",
                depends="flip-coin",
            )
            Task(
                name="tails",
                template="tails",
                when="{{tasks.flip-coin.outputs.result}} == tails",
                depends="flip-coin",
            )
        Script(
            name="flip-coin",
            command=["python"],
            image="python:alpine3.6",
            source='import random\nprint("heads" if random.randint(0,1) == 0 else "tails")\n',
        )
        Script(
            name="heads",
            outputs=Outputs(
                artifacts=[
                    Artifact(
                        name="result",
                        path="/result.txt",
                    )
                ],
            ),
            command=["python"],
            image="python:alpine3.6",
            source='with open("result.txt", "w") as f:\n  f.write("it was heads")\n',
        )
        Script(
            name="tails",
            outputs=Outputs(
                artifacts=[
                    Artifact(
                        name="result",
                        path="/result.txt",
                    )
                ],
            ),
            command=["python"],
            image="python:alpine3.6",
            source='with open("result.txt", "w") as f:\n  f.write("it was tails")\n',
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dag-conditional-artifacts-
      annotations:
        workflows.argoproj.io/description: |
          Conditional artifacts provides a way to choose the output artifacts based on an expression.

          In this example the DAG template has two tasks which will run conditionall using `when`.

          Based on the condition one of steps may not execute. The step template output's artifact will be set to the
          executed step's output artifacts.
        workflows.argoproj.io/version: '>= 3.1.0'
      labels:
        workflows.argoproj.io/test: 'true'
    spec:
      entrypoint: main
      templates:
      - name: main
        dag:
          tasks:
          - name: flip-coin
            template: flip-coin
          - name: heads
            depends: flip-coin
            template: heads
            when: '{{tasks.flip-coin.outputs.result}} == heads'
          - name: tails
            depends: flip-coin
            template: tails
            when: '{{tasks.flip-coin.outputs.result}} == tails'
        outputs:
          artifacts:
          - name: result
            fromExpression: 'tasks[''flip-coin''].outputs.result == ''heads'' ? tasks.heads.outputs.artifacts.result
              : tasks.tails.outputs.artifacts.result'
      - name: flip-coin
        script:
          image: python:alpine3.6
          source: |
            import random
            print("heads" if random.randint(0,1) == 0 else "tails")
          command:
          - python
      - name: heads
        outputs:
          artifacts:
          - name: result
            path: /result.txt
        script:
          image: python:alpine3.6
          source: |
            with open("result.txt", "w") as f:
              f.write("it was heads")
          command:
          - python
      - name: tails
        outputs:
          artifacts:
          - name: result
            path: /result.txt
        script:
          image: python:alpine3.6
          source: |
            with open("result.txt", "w") as f:
              f.write("it was tails")
          command:
          - python
    ```

