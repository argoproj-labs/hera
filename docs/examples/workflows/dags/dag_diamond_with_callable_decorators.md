# Dag Diamond With Callable Decorators






=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        DAG,
        Workflow,
        script,
    )


    @script(add_cwd_to_sys_path=False, image="python:alpine3.6")
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
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: message
                value: A
            name: A
            template: echo
          - arguments:
              parameters:
              - name: message
                value: B
            depends: A
            name: B
            template: echo
          - arguments:
              parameters:
              - name: message
                value: C
            depends: A
            name: C
            template: echo
          - arguments:
              parameters:
              - name: message
                value: D
            depends: B && C
            name: D
            template: echo
        name: diamond
      - inputs:
          parameters:
          - name: message
        name: echo
        script:
          command:
          - python
          image: python:alpine3.6
          source: 'import json

            try: message = json.loads(r''''''{{inputs.parameters.message}}'''''')

            except: message = r''''''{{inputs.parameters.message}}''''''


            print(message)'
    ```

