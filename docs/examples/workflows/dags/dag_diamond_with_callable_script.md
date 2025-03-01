# Dag Diamond With Callable Script






=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Workflow, script


    @script(image="python:3.12")
    def echo(message):
        print(message)


    with Workflow(generate_name="dag-diamond-", entrypoint="diamond") as w:
        with DAG(name="diamond"):
            A = echo(name="A", arguments={"message": "A"})
            B = echo(name="B", arguments={"message": "B"})
            C = echo(name="C", arguments={"message": "C"})
            D = echo(name="D", arguments={"message": "D"})
            A >> [B, C] >> D
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dag-diamond-
    spec:
      entrypoint: diamond
      templates:
      - name: diamond
        dag:
          tasks:
          - name: A
            template: echo
            arguments:
              parameters:
              - name: message
                value: A
          - name: B
            depends: A
            template: echo
            arguments:
              parameters:
              - name: message
                value: B
          - name: C
            depends: A
            template: echo
            arguments:
              parameters:
              - name: message
                value: C
          - name: D
            depends: B && C
            template: echo
            arguments:
              parameters:
              - name: message
                value: D
      - name: echo
        inputs:
          parameters:
          - name: message
        script:
          image: python:3.12
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: message = json.loads(r'''{{inputs.parameters.message}}''')
            except: message = r'''{{inputs.parameters.message}}'''

            print(message)
          command:
          - python
    ```

