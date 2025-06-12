# Default Parameters



This example shows script function default parameters.

Script functions parameters mirror Python's behaviour:

* use the caller argument value if provided
* otherwise use the default if provided
* otherwise error as no value provided (and a value is always required in Argo Workflows)


=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Workflow, script


    @script()
    def generator():
        print("Another message for the world!")


    @script()
    def consumer(message: str = "Hello, world!", foo: int = 42):
        print(message)
        print(foo)


    with Workflow(generate_name="default-param-overwrite-", entrypoint="d") as w:
        with DAG(name="d"):
            g = generator()
            c_default = consumer(name="consume-default")
            c_arg = consumer(name="consume-argument", arguments={"message": g.result})
            g >> [c_default, c_arg]
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
      - name: d
        dag:
          tasks:
          - name: generator
            template: generator
          - name: consume-default
            depends: generator
            template: consumer
          - name: consume-argument
            depends: generator
            template: consumer
            arguments:
              parameters:
              - name: message
                value: '{{tasks.generator.outputs.result}}'
      - name: generator
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print('Another message for the world!')
          command:
          - python
      - name: consumer
        inputs:
          parameters:
          - name: message
            default: Hello, world!
          - name: foo
            default: '42'
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: foo = json.loads(r'''{{inputs.parameters.foo}}''')
            except: foo = r'''{{inputs.parameters.foo}}'''
            try: message = json.loads(r'''{{inputs.parameters.message}}''')
            except: message = r'''{{inputs.parameters.message}}'''

            print(message)
            print(foo)
          command:
          - python
    ```

