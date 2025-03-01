# Coinflip






=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Workflow, script


    @script()
    def flip():
        import random

        result = "heads" if random.randint(0, 1) == 0 else "tails"
        print(result)


    @script()
    def heads():
        print("it was heads")


    @script()
    def tails():
        print("it was tails")


    with Workflow(generate_name="coinflip-", entrypoint="d") as w:
        with DAG(name="d") as s:
            f = flip()
            heads().on_other_result(f, "heads")
            tails().on_other_result(f, "tails")
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: coinflip-
    spec:
      entrypoint: d
      templates:
      - name: d
        dag:
          tasks:
          - name: flip
            template: flip
          - name: heads
            depends: flip
            template: heads
            when: '{{tasks.flip.outputs.result}} == heads'
          - name: tails
            depends: flip
            template: tails
            when: '{{tasks.flip.outputs.result}} == tails'
      - name: flip
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import random
            result = 'heads' if random.randint(0, 1) == 0 else 'tails'
            print(result)
          command:
          - python
      - name: heads
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print('it was heads')
          command:
          - python
      - name: tails
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print('it was tails')
          command:
          - python
    ```

