# Dag Conditional Parameters

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-conditional-parameters.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.expr import g
    from hera.workflows import DAG, Parameter, Script, Task, Workflow


    def heads():
        print("heads")


    def tails():
        print("tails")


    def flip_coin():
        import random

        print("heads" if random.randint(0, 1) == 0 else "tails")


    def get_script(callable):
        return Script(
            name=callable.__name__.replace("_", "-"),
            source=callable,
            add_cwd_to_sys_path=False,
            image="python:alpine3.6",
        )


    with Workflow(
        generate_name="dag-conditional-parameter-",
        entrypoint="main",
    ) as w:
        heads_template = get_script(heads)
        tails_template = get_script(tails)
        flip_coin_template = get_script(flip_coin)

        with DAG(name="main") as main_dag:
            flip_coin_task = Task(name="flip-coin", template=flip_coin_template)
            heads_task = Task(name="heads", template=heads_template)
            tails_task = Task(name="tails", template=tails_template)
            heads_task.on_other_result(flip_coin_task, "heads")
            tails_task.on_other_result(flip_coin_task, "tails")

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
      - name: heads
        script:
          command:
          - python
          image: python:alpine3.6
          source: print('heads')
      - name: tails
        script:
          command:
          - python
          image: python:alpine3.6
          source: print('tails')
      - name: flip-coin
        script:
          command:
          - python
          image: python:alpine3.6
          source: 'import random

            print((''heads'' if (random.randint(0, 1) == 0) else ''tails''))'
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
    ```

