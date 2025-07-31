# Map Outputs To Inputs






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


    @script(
        outputs=[
            Parameter(name="a", value_from=m.ValueFrom(path="/a")),
            Parameter(name="b", value_from=m.ValueFrom(path="/b")),
            Parameter(name="c", value_from=m.ValueFrom(path="/c")),
        ]
    )
    def create_some_outputs():
        outputs = ["a", "b", "c"]
        for output in outputs:
            with open(f"/{output}", "w") as f_out:
                f_out.write(f"This is {output}")


    @script(
        outputs=[
            Parameter(name="d", value_from=m.ValueFrom(path="/d")),
            Parameter(name="e", value_from=m.ValueFrom(path="/e")),
        ]
    )
    def create_more_outputs():
        outputs = ["d", "e"]
        for output in outputs:
            with open(f"/{output}", "w") as f_out:
                f_out.write(f"This is {output}")


    @script()
    def use_some_inputs(a, b, c):
        print(a, b, c)


    @script()
    def use_more_inputs(a, b, c, d, e):
        print(a, b, c, d, e)


    with Workflow(generate_name="map-outputs-to-inputs-", entrypoint="dag") as w:
        with DAG(name="dag"):
            t1: Task = create_some_outputs()
            t2 = use_some_inputs(arguments=t1.get_outputs_as_arguments())

            t3: Task = create_more_outputs()
            t4 = use_more_inputs(arguments=t1.get_outputs_as_arguments() + t3.get_outputs_as_arguments())

            t1 >> t2
            [t1, t3] >> t4
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: map-outputs-to-inputs-
    spec:
      entrypoint: dag
      templates:
      - name: dag
        dag:
          tasks:
          - name: create-some-outputs
            template: create-some-outputs
          - name: use-some-inputs
            depends: create-some-outputs
            template: use-some-inputs
            arguments:
              parameters:
              - name: a
                value: '{{tasks.create-some-outputs.outputs.parameters.a}}'
              - name: b
                value: '{{tasks.create-some-outputs.outputs.parameters.b}}'
              - name: c
                value: '{{tasks.create-some-outputs.outputs.parameters.c}}'
          - name: create-more-outputs
            template: create-more-outputs
          - name: use-more-inputs
            depends: create-some-outputs && create-more-outputs
            template: use-more-inputs
            arguments:
              parameters:
              - name: a
                value: '{{tasks.create-some-outputs.outputs.parameters.a}}'
              - name: b
                value: '{{tasks.create-some-outputs.outputs.parameters.b}}'
              - name: c
                value: '{{tasks.create-some-outputs.outputs.parameters.c}}'
              - name: d
                value: '{{tasks.create-more-outputs.outputs.parameters.d}}'
              - name: e
                value: '{{tasks.create-more-outputs.outputs.parameters.e}}'
      - name: create-some-outputs
        outputs:
          parameters:
          - name: a
            valueFrom:
              path: /a
          - name: b
            valueFrom:
              path: /b
          - name: c
            valueFrom:
              path: /c
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            outputs = ['a', 'b', 'c']
            for output in outputs:
                with open(f'/{output}', 'w') as f_out:
                    f_out.write(f'This is {output}')
          command:
          - python
      - name: use-some-inputs
        inputs:
          parameters:
          - name: a
          - name: b
          - name: c
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: a = json.loads(r'''{{inputs.parameters.a}}''')
            except: a = r'''{{inputs.parameters.a}}'''
            try: b = json.loads(r'''{{inputs.parameters.b}}''')
            except: b = r'''{{inputs.parameters.b}}'''
            try: c = json.loads(r'''{{inputs.parameters.c}}''')
            except: c = r'''{{inputs.parameters.c}}'''

            print(a, b, c)
          command:
          - python
      - name: create-more-outputs
        outputs:
          parameters:
          - name: d
            valueFrom:
              path: /d
          - name: e
            valueFrom:
              path: /e
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            outputs = ['d', 'e']
            for output in outputs:
                with open(f'/{output}', 'w') as f_out:
                    f_out.write(f'This is {output}')
          command:
          - python
      - name: use-more-inputs
        inputs:
          parameters:
          - name: a
          - name: b
          - name: c
          - name: d
          - name: e
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: a = json.loads(r'''{{inputs.parameters.a}}''')
            except: a = r'''{{inputs.parameters.a}}'''
            try: b = json.loads(r'''{{inputs.parameters.b}}''')
            except: b = r'''{{inputs.parameters.b}}'''
            try: c = json.loads(r'''{{inputs.parameters.c}}''')
            except: c = r'''{{inputs.parameters.c}}'''
            try: d = json.loads(r'''{{inputs.parameters.d}}''')
            except: d = r'''{{inputs.parameters.d}}'''
            try: e = json.loads(r'''{{inputs.parameters.e}}''')
            except: e = r'''{{inputs.parameters.e}}'''

            print(a, b, c, d, e)
          command:
          - python
    ```

