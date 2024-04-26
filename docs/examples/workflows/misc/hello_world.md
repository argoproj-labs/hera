# Hello World






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Workflow, script


    @script()
    def hello(s: str):
        print("Hello, {s}!".format(s=s))


    with Workflow(
        generate_name="hello-world-",
        entrypoint="hello",
        arguments={"s": "world"},
    ) as w:
        hello()
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: hello-world-
    spec:
      arguments:
        parameters:
        - name: s
          value: world
      entrypoint: hello
      templates:
      - inputs:
          parameters:
          - name: s
        name: hello
        script:
          command:
          - python
          image: python:3.8
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: s = json.loads(r'''{{inputs.parameters.s}}''')
            except: s = r'''{{inputs.parameters.s}}'''

            print('Hello, {s}!'.format(s=s))
    ```

