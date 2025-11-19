# Passing Task Result



This example shows how to pass the `result` output parameter between tasks.


=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Task, Workflow, script


    @script()
    def out():
        print(42)


    @script()
    def in_(a):
        print(a)


    with Workflow(generate_name="script-param-passing-", entrypoint="d") as w:
        with DAG(name="d"):
            t1: Task = out()
            t2 = in_(arguments={"a": t1.result})
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
      - name: d
        dag:
          tasks:
          - name: out
            template: out
          - name: in-
            depends: out
            template: in-
            arguments:
              parameters:
              - name: a
                value: '{{tasks.out.outputs.result}}'
      - name: out
        script:
          image: python:3.10
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print(42)
          command:
          - python
      - name: in-
        inputs:
          parameters:
          - name: a
        script:
          image: python:3.10
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: a = json.loads(r'''{{inputs.parameters.a}}''')
            except: a = r'''{{inputs.parameters.a}}'''

            print(a)
          command:
          - python
    ```

