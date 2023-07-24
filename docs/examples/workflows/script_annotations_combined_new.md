# Script Annotations Combined New






=== "Hera"

    ```python linenums="1"
    try:
        from typing import Annotated  # type: ignore
    except ImportError:
        from typing_extensions import Annotated  # type: ignore

    from hera.shared import global_config
    from hera.workflows import Workflow, script
    from hera.workflows.parameter import Parameter
    from hera.workflows.steps import Steps

    global_config.experimental_features["script_annotations"] = True


    @script()
    def echo_all(
        an_int: Annotated[int, Parameter(description="an_int parameter", default=1, enum=[1, 2, 3])],
        a_bool: Annotated[bool, Parameter(description="a_bool parameter", default=True, enum=[True, False])],
        a_string: Annotated[str, Parameter(description="a_string parameter", default="a", enum=["a", "b", "c"])],
    ):
        print(an_int)
        print(a_bool)
        print(a_string)


    with Workflow(generate_name="test-types-", entrypoint="my_steps") as w:
        with Steps(name="my_steps") as s:
            echo_all(arguments={"an_int": 1, "a_bool": True, "a_string": "a"})
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
              - name: a_bool
                value: 'true'
              - name: a_string
                value: a
            name: echo-all
            template: echo-all
      - inputs:
          parameters:
          - default: '1'
            description: an_int parameter
            enum:
            - '1'
            - '2'
            - '3'
            name: an_int
          - default: 'true'
            description: a_bool parameter
            enum:
            - 'True'
            - 'False'
            name: a_bool
          - default: a
            description: a_string parameter
            enum:
            - a
            - b
            - c
            name: a_string
        name: echo-all
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

            try: a_string = json.loads(r''''''{{inputs.parameters.a_string}}'''''')

            except: a_string = r''''''{{inputs.parameters.a_string}}''''''

            try: an_int = json.loads(r''''''{{inputs.parameters.an_int}}'''''')

            except: an_int = r''''''{{inputs.parameters.an_int}}''''''


            print(an_int)

            print(a_bool)

            print(a_string)'
    ```

