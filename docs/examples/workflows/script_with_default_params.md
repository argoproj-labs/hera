# Script With Default Params






=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Workflow, script


    @script()
    def foo(a, b=42, c=None):
        print(a, b, c)


    with Workflow(generate_name="script-default-params-", entrypoint="d") as w:
        with DAG(name="d"):
            foo(name="b-unset-c-unset", arguments={"a": 1})
            foo(name="b-set-c-unset", arguments={"a": 1, "b": 2})
            foo(name="b-unset-c-set", arguments={"a": 1, "c": 2})
            foo(name="b-set-c-set", arguments={"a": 1, "b": 2, "c": 3})
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
            name: b-unset-c-unset
            template: foo
          - arguments:
              parameters:
              - name: a
                value: '1'
              - name: b
                value: '2'
            name: b-set-c-unset
            template: foo
          - arguments:
              parameters:
              - name: a
                value: '1'
              - name: c
                value: '2'
            name: b-unset-c-set
            template: foo
          - arguments:
              parameters:
              - name: a
                value: '1'
              - name: b
                value: '2'
              - name: c
                value: '3'
            name: b-set-c-set
            template: foo
        name: d
      - inputs:
          parameters:
          - name: a
          - default: '42'
            name: b
          - default: 'null'
            name: c
        name: foo
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

            try: b = json.loads(r''''''{{inputs.parameters.b}}'''''')

            except: b = r''''''{{inputs.parameters.b}}''''''

            try: c = json.loads(r''''''{{inputs.parameters.c}}'''''')

            except: c = r''''''{{inputs.parameters.c}}''''''


            print(a, b, c)'
    ```

