# Script Annotations Alias






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
    def echo(
        a_name: Annotated[str, Parameter(name="another_name")],
    ):
        print(a_name)


    with Workflow(generate_name="test-types-", entrypoint="my_steps") as w:
        with Steps(name="my_steps") as s:
            echo(arguments={"a_name": "hello there"})
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
              - name: a_name
                value: hello there
            name: echo
            template: echo
      - inputs:
          parameters:
          - name: another_name
        name: echo
        script:
          command:
          - python
          env:
          - name: script_annotations
            value: ''
          image: python:3.8
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            import json

            try: another_name = json.loads(r''''''{{inputs.parameters.another_name}}'''''')

            except: another_name = r''''''{{inputs.parameters.another_name}}''''''


            print(a_name)'
    ```

