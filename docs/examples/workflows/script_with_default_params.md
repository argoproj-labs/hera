# Script With Default Params






=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Workflow, script


    @script()
    def foo(a, b=42):
        print(a, b)


    with Workflow(generate_name="script-default-params-", entrypoint="d") as w:
        with DAG(name="d"):
            foo(name="b-set", arguments={"a": 1, "b": 2})
            foo(name="b-unset", arguments={"a": 1})
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: script-default-params-
    spec:
      entrypoint: d
      templates:
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: a
                value: '1'
              - name: b
                value: '2'
            name: b-set
            template: foo
          - arguments:
              parameters:
              - name: a
                value: '1'
            name: b-unset
            template: foo
        name: d
      - inputs:
          parameters:
          - name: a
          - default: '42'
            name: b
        name: foo
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

            try: b = json.loads(r''''''{{inputs.parameters.b}}'''''')

            except: b = r''''''{{inputs.parameters.b}}''''''


            print(a, b)

            '
    ```

