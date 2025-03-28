# Recursive Dag






=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Task, Workflow, script


    @script()
    def random_roll():
        import random

        print(random.randint(1, 6))


    with Workflow(generate_name="recursive-dag-", entrypoint="dag") as w:
        with DAG(name="dag") as dag:
            random_number = random_roll(name="roll")
            recurse = Task(
                name="recurse-if-not-six",
                template=dag,
                when=f"{random_number.result} != 6",
            )
            random_number >> recurse
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: recursive-dag-
    spec:
      entrypoint: dag
      templates:
      - name: dag
        dag:
          tasks:
          - name: roll
            template: random-roll
          - name: recurse-if-not-six
            depends: roll
            template: dag
            when: '{{tasks.roll.outputs.result}} != 6'
      - name: random-roll
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import random
            print(random.randint(1, 6))
          command:
          - python
    ```

