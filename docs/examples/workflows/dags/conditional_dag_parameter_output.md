# Conditional Dag Parameter Output



This example shows how a DAG can output a value from an expression (using the `hera.expr` module).


=== "Hera"

    ```python linenums="1"
    from hera.expr import g
    from hera.workflows import DAG, Parameter, Workflow, script


    @script()
    def heads():
        print("heads")


    @script()
    def tails():
        print("tails")


    @script()
    def flip_coin():
        import random

        print("heads" if random.randint(0, 1) == 0 else "tails")


    with Workflow(
        generate_name="dag-conditional-parameter-",
        entrypoint="main",
    ) as w:
        with DAG(name="main") as main_dag:
            fc = flip_coin(name="flip-coin")
            h = heads(name="heads").on_other_result(fc, "heads")
            t = tails(name="tails").on_other_result(fc, "tails")

            expression = g.tasks["flip-coin"].outputs.result == "heads"
            expression = expression.check(g.tasks.heads.outputs.result, g.tasks.tails.outputs.result)  # type: ignore
            main_dag.outputs = [Parameter(name="stepresult", value_from={"expression": str(expression)})]
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dag-conditional-parameter-
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
          parameters:
          - name: stepresult
            valueFrom:
              expression: 'tasks[''flip-coin''].outputs.result == ''heads'' ? tasks.heads.outputs.result
                : tasks.tails.outputs.result'
      - name: flip-coin
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import random
            print('heads' if random.randint(0, 1) == 0 else 'tails')
          command:
          - python
      - name: heads
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print('heads')
          command:
          - python
      - name: tails
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print('tails')
          command:
          - python
    ```

