# Default Param Overwrite



This example showcases how a Python source can be scheduled with default parameters as kwargs but overwritten
conditionally.


=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Workflow, script


    @script()
    def generator():
        print("Another message for the world!")


    @script()
    def consumer(message: str = "Hello, world!"):
        print(message)


    with Workflow(generate_name="default-param-overwrite-", entrypoint="d") as w:
        with DAG(name="d"):
            g = generator()
            c_default = consumer(name="consumer-default")
            c_param = consumer(name="consumer-param", arguments=g.get_result_as("message"))
            g >> [c_default, c_param]
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: default-param-overwrite-
    spec:
      entrypoint: d
      templates:
      - dag:
          tasks:
          - name: generator
            template: generator
          - depends: generator
            name: consumer-default
            template: consumer
          - arguments:
              parameters:
              - name: message
                value: '{{tasks.generator.outputs.result}}'
            depends: generator
            name: consumer-param
            template: consumer
        name: d
      - name: generator
        script:
          command:
          - python
          image: python:3.8
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print('Another message for the world!')
      - inputs:
          parameters:
          - default: Hello, world!
            name: message
        name: consumer
        script:
          command:
          - python
          image: python:3.8
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: message = json.loads(r'''{{inputs.parameters.message}}''')
            except: message = r'''{{inputs.parameters.message}}'''

            print(message)
    ```

