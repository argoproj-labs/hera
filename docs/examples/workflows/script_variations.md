# Script Variations






=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Workflow, script


    @script()
    def hello_world():  # pragma: no cover
        print("Hello World!")


    @script()
    def multiline_function(test: str, another_test: str):  # pragma: no cover
        print(test)
        print(another_test)


    with Workflow(generate_name="fv-test-", entrypoint="d") as w:
        with DAG(name="d"):
            hello_world()
            multiline_function(arguments={"test": "test string", "another_test": "another test string"})
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: fv-test-
    spec:
      entrypoint: d
      templates:
      - dag:
          tasks:
          - name: hello-world
            template: hello-world
          - arguments:
              parameters:
              - name: test
                value: test string
              - name: another_test
                value: another test string
            name: multiline-function
            template: multiline-function
        name: d
      - name: hello-world
        script:
          command:
          - python
          image: python:3.8
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            print(''Hello World!'')'
      - inputs:
          parameters:
          - name: test
          - name: another_test
        name: multiline-function
        script:
          command:
          - python
          image: python:3.8
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            import json

            try: another_test = json.loads(r''''''{{inputs.parameters.another_test}}'''''')

            except: another_test = r''''''{{inputs.parameters.another_test}}''''''

            try: test = json.loads(r''''''{{inputs.parameters.test}}'''''')

            except: test = r''''''{{inputs.parameters.test}}''''''


            print(test)

            print(another_test)'
    ```

