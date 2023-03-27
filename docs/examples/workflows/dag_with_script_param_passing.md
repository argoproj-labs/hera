# Dag With Script Param Passing






=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Parameter, Task, Workflow, script


    @script()
    def out():
        print(42)


    @script()
    def in_(a):
        print(a)


    with Workflow(generate_name="script-param-passing-", entrypoint="d") as w:
        with DAG(name="d"):
            t1: Task = out()
            t2 = in_(arguments=Parameter(name="a", value=t1.result))
            t1 >> t2
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: script-param-passing-
    spec:
      entrypoint: d
      templates:
      - dag:
          tasks:
          - name: out
            template: out
          - arguments:
              parameters:
              - name: a
                value: '{{tasks.out.outputs.result}}'
            depends: out
            name: in-
            template: in-
        name: d
      - name: out
        script:
          command:
          - python
          image: python:3.7
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            print(42)

            '
      - inputs:
          parameters:
          - name: a
        name: in-
        script:
          command:
          - python
          image: python:3.7
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            import json

            try: a = json.loads(r''''''{{inputs.parameters.a}}'''''')

            except: a = r''''''{{inputs.parameters.a}}''''''


            print(a)

            '
    ```

