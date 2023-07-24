# Script Annotations Default Both






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
    def echo_new(an_int: Annotated[int, Parameter(default=1)]):
        print(an_int)


    # note that you can use the Annotated for other fields and the Python default
    @script()
    def echo_old(an_int: Annotated[int, Parameter(name="another_name")] = 1):
        print(an_int)


    with Workflow(generate_name="test-types-", entrypoint="my_steps") as w:
        with Steps(name="my_steps") as s:
            echo_new(arguments={"an_int": 1})
            echo_old(arguments={"an_int": 1})
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
            name: echo-new
            template: echo-new
        - - arguments:
              parameters:
              - name: an_int
                value: '1'
            name: echo-old
            template: echo-old
      - inputs:
          parameters:
          - default: '1'
            name: an_int
        name: echo-new
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
          - default: '1'
            name: another_name
        name: echo-old
        script:
          command:
          - python
          image: python:3.8
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            import json

            try: another_name = json.loads(r''''''{{inputs.parameters.another_name}}'''''')

            except: another_name = r''''''{{inputs.parameters.another_name}}''''''


            print(an_int)'
    ```

