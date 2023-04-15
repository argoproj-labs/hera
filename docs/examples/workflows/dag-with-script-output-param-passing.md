# Dag-With-Script-Output-Param-Passing






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
      - dag:
          tasks:
          - name: out
            template: out
          - arguments:
              parameters:
              - name: a
                value: '{{tasks.out.outputs.parameters.a}}'
            depends: out
            name: in-
            template: in-
        name: d
      - name: out
        outputs:
          parameters:
          - name: a
            valueFrom:
              path: /test
        script:
          command:
          - python
          image: python:3.8
          source: "import os\nimport sys\nsys.path.append(os.getcwd())\nwith open('/test',\
            \ 'w') as f_out:\n    f_out.write('test')"
      - inputs:
          parameters:
          - name: a
        name: in-
        script:
          command:
          - python
          image: python:3.8
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            import json

            try: a = json.loads(r''''''{{inputs.parameters.a}}'''''')

            except: a = r''''''{{inputs.parameters.a}}''''''


            print(a)'
    ```

