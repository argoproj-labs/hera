# Script Annotations Enum Old






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Workflow, script
    from hera.workflows.parameter import Parameter
    from hera.workflows.steps import Steps


    @script(inputs=[Parameter(name="an_int", enum=[1, 2, 3])])
    def echo_int(an_int):
        print(an_int)


    @script(inputs=[Parameter(name="a_bool", enum=[True])])
    def echo_boolean(a_bool):
        print(a_bool)


    @script(inputs=[Parameter(name="a_string", enum=["a", "b", "c"])])
    def echo_string(a_string):
        print(a_string)


    with Workflow(generate_name="test-types-", entrypoint="my_steps") as w:
        with Steps(name="my_steps") as s:
            echo_int(arguments={"an_int": 1})
            echo_boolean(arguments={"a_bool": True})
            echo_string(arguments={"a_string": "a"})
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: test-types-
    spec:
      entrypoint: my_steps
      templates:
      - name: my_steps
        steps:
        - - arguments:
              parameters:
              - name: an_int
                value: '1'
            name: echo-int
            template: echo-int
        - - arguments:
              parameters:
              - name: a_bool
                value: 'true'
            name: echo-boolean
            template: echo-boolean
        - - arguments:
              parameters:
              - name: a_string
                value: a
            name: echo-string
            template: echo-string
      - inputs:
          parameters:
          - enum:
            - '1'
            - '2'
            - '3'
            name: an_int
        name: echo-int
        script:
          command:
          - python
          image: python:3.8
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            import json

            try: an_int = json.loads(r''''''{{inputs.parameters.an_int}}'''''')

            except: an_int = r''''''{{inputs.parameters.an_int}}''''''


            print(an_int)'
      - inputs:
          parameters:
          - enum:
            - 'True'
            name: a_bool
        name: echo-boolean
        script:
          command:
          - python
          image: python:3.8
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            import json

            try: a_bool = json.loads(r''''''{{inputs.parameters.a_bool}}'''''')

            except: a_bool = r''''''{{inputs.parameters.a_bool}}''''''


            print(a_bool)'
      - inputs:
          parameters:
          - enum:
            - a
            - b
            - c
            name: a_string
        name: echo-string
        script:
          command:
          - python
          image: python:3.8
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            import json

            try: a_string = json.loads(r''''''{{inputs.parameters.a_string}}'''''')

            except: a_string = r''''''{{inputs.parameters.a_string}}''''''


            print(a_string)'
    ```

