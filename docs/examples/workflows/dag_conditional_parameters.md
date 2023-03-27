# Dag Conditional Parameters






=== "Hera"

    ```python linenums="1"
    from hera.expr import g
    from hera.workflows import DAG, Parameter, Workflow, script


    @script(add_cwd_to_sys_path=False, image="python:alpine3.6")
    def heads():
        print("heads")


    @script(add_cwd_to_sys_path=False, image="python:alpine3.6")
    def tails():
        print("tails")


    @script(add_cwd_to_sys_path=False, image="python:alpine3.6")
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
      - dag:
          tasks:
          - name: flip-coin
            template: flip-coin
          - depends: flip-coin
            name: heads
            template: heads
            when: '{{tasks.flip-coin.outputs.result}} == heads'
          - depends: flip-coin
            name: tails
            template: tails
            when: '{{tasks.flip-coin.outputs.result}} == tails'
        name: main
        outputs:
          parameters:
          - name: stepresult
            valueFrom:
              expression: 'tasks[''flip-coin''].outputs.result == ''heads'' ? tasks.heads.outputs.result
                : tasks.tails.outputs.result'
      - name: flip-coin
        script:
          command:
          - python
          image: python:alpine3.6
          source: 'import random


            print("heads" if random.randint(0, 1) == 0 else "tails")

            '
      - name: heads
        script:
          command:
          - python
          image: python:alpine3.6
          source: 'print("heads")

            '
      - name: tails
        script:
          command:
          - python
          image: python:alpine3.6
          source: 'print("tails")

            '
    ```

