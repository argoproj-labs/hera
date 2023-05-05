# Hello World






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Script, Workflow


    def hello(s: str):
        print(f"Hello, {s}!")


    with Workflow(generate_name="task-exit-handler-", entrypoint="s") as w:
        Script(name="s", source=hello, inputs={"s": "world"})
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: task-exit-handler-
    spec:
      entrypoint: s
      templates:
      - inputs:
          parameters:
          - name: s
            value: world
        name: s
        script:
          command:
          - python
          image: python:3.8
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            import json

            try: s = json.loads(r''''''{{inputs.parameters.s}}'''''')

            except: s = r''''''{{inputs.parameters.s}}''''''


            print(f''Hello, {s}!'')'
    ```

