# Dag Coinflip

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-coinflip.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, Script, Step, Steps, Task, Workflow

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        annotations={"workflows.argoproj.io/description": "This is an example of coin flip defined as a DAG.\n"},
        generate_name="dag-diamond-coinflip-",
        entrypoint="diamond",
    ) as w:
        with DAG(
            name="diamond",
        ) as invocator:
            Task(
                name="A",
                template="coinflip",
            )
            Task(
                name="B",
                template="coinflip",
                depends="A",
            )
            Task(
                name="C",
                template="coinflip",
                depends="A",
            )
            Task(
                name="D",
                template="coinflip",
                depends="B && C",
            )
        with Steps(
            name="coinflip",
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
                    template="coinflip",
                    when="{{steps.flip-coin.outputs.result}} == tails",
                )
        Script(
            name="flip-coin",
            command=["python"],
            image="python:alpine3.6",
            source='import random\nresult = "heads" if random.randint(0,1) == 0 else "tails"\nprint(result)\n',
        )
        Container(
            name="heads",
            args=['echo "it was heads"'],
            command=["sh", "-c"],
            image="alpine:3.6",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dag-diamond-coinflip-
      annotations:
        workflows.argoproj.io/description: |
          This is an example of coin flip defined as a DAG.
    spec:
      entrypoint: diamond
      templates:
      - name: diamond
        dag:
          tasks:
          - name: A
            template: coinflip
          - name: B
            depends: A
            template: coinflip
          - name: C
            depends: A
            template: coinflip
          - name: D
            depends: B && C
            template: coinflip
      - name: coinflip
        steps:
        - - name: flip-coin
            template: flip-coin
        - - name: heads
            template: heads
            when: '{{steps.flip-coin.outputs.result}} == heads'
          - name: tails
            template: coinflip
            when: '{{steps.flip-coin.outputs.result}} == tails'
      - name: flip-coin
        script:
          image: python:alpine3.6
          source: |
            import random
            result = "heads" if random.randint(0,1) == 0 else "tails"
            print(result)
          command:
          - python
      - name: heads
        container:
          image: alpine:3.6
          args:
          - echo "it was heads"
          command:
          - sh
          - -c
    ```

