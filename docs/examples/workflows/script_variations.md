# Script Variations






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Workflow, script


    @script()
    def hello_world():  # pragma: no cover
        print("Hello World!")


    @script()
    def multiline_function(
        test: str,
        another_test: str,
    ) -> str:  # pragma: no cover
        print("Hello World!")


    with Workflow(generate_name="fv-test-", entrypoint="d") as w:
        hello_world()
        multiline_function()
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


            print(''Hello World!'')'
    ```

