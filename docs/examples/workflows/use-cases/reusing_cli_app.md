# Reusing Cli App



This example shows how a CLI application built with [Cappa](https://github.com/DanCardin/cappa) can also be used as a `script` function.

!!! Warning
    Using the `script` decorator is not possible with other CLI libraries like [`click`](https://click.palletsprojects.com/en/stable/), and will require use of the `Script` class and setting `source=function_name`.
    [See this issue discussion](https://github.com/argoproj-labs/hera/issues/1530#issuecomment-3616082722) for more details.


=== "Hera"

    ```python linenums="1"
    import cappa

    from hera.workflows import Workflow, script


    @script()
    def hello(count: int, name: str):
        """Simple program that greets NAME for a total of COUNT times."""
        for _ in range(count):
            print(f"Hello {name}!")


    with Workflow(
        generate_name="cli-example-",
        entrypoint="hello",
        arguments={"count": 3, "name": "Hera"},
    ) as w:
        hello()


    if __name__ == "__main__":
        cappa.invoke(hello)
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: cli-example-
    spec:
      entrypoint: hello
      templates:
      - name: hello
        inputs:
          parameters:
          - name: count
          - name: name
        script:
          image: python:3.10
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: count = json.loads(r'''{{inputs.parameters.count}}''')
            except: count = r'''{{inputs.parameters.count}}'''
            try: name = json.loads(r'''{{inputs.parameters.name}}''')
            except: name = r'''{{inputs.parameters.name}}'''

            """Simple program that greets NAME for a total of COUNT times."""
            for _ in range(count):
                print(f'Hello {name}!')
          command:
          - python
      arguments:
        parameters:
        - name: count
          value: '3'
        - name: name
          value: Hera
    ```

