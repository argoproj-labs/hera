# Script Annotations Default Old






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Workflow, script
    from hera.workflows.steps import Steps


    @script()
    def echo_int(an_int=1):
        print(an_int)


    @script()
    def echo_boolean(a_bool=True):
        print(a_bool)


    @script()
    def echo_string(a_string="a"):
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
          - default: '1'
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
          - default: 'true'
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
          - default: a
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

