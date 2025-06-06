# Output Parameters






=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        DAG,
        Parameter,
        Task,
        Workflow,
        models as m,
        script,
    )


    @script(outputs=[Parameter(name="a", value_from=m.ValueFrom(path="/test"))])
    def out():
        with open("/test", "w") as f_out:
            f_out.write("test")


    @script()
    def in_(a):
        print(a)


    with Workflow(generate_name="script-output-param-passing-", entrypoint="d") as w:
        with DAG(name="d"):
            t1: Task = out()
            t2 = in_(arguments=t1.get_parameter("a"))
            t1 >> t2
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: script-output-param-passing-
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
                value: '{{tasks.out.outputs.parameters.a}}'
      - name: out
        outputs:
          parameters:
          - name: a
            valueFrom:
              path: /test
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            with open('/test', 'w') as f_out:
                f_out.write('test')
          command:
          - python
      - name: in-
        inputs:
          parameters:
          - name: a
        script:
          image: python:3.9
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

