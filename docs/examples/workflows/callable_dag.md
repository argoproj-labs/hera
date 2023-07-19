# Callable Dag






=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Parameter, Workflow, script


    @script()
    def hello(name: str):
        print("Hello, {name}!".format(name=name))


    with Workflow(
        generate_name="callable-dag-",
        entrypoint="calling-dag",
    ) as w:
        with DAG(name="my-dag", inputs=Parameter(name="my-dag-input")) as my_dag:
            hello(name="hello-1", arguments={"name": "hello-1-{{inputs.parameters.my-dag-input}}"})
            hello(name="hello-2", arguments={"name": "hello-2-{{inputs.parameters.my-dag-input}}"})

        with DAG(name="calling-dag") as d:
            t1 = my_dag(name="call-1", arguments={"my-dag-input": "call-1"})
            t2 = my_dag(name="call-2", arguments={"my-dag-input": "call-2"})
            t1 >> t2
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: callable-dag-
    spec:
      entrypoint: calling-dag
      templates:
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: name
                value: hello-1-{{inputs.parameters.my-dag-input}}
            name: hello-1
            template: hello
          - arguments:
              parameters:
              - name: name
                value: hello-2-{{inputs.parameters.my-dag-input}}
            name: hello-2
            template: hello
        inputs:
          parameters:
          - name: my-dag-input
        name: my-dag
      - inputs:
          parameters:
          - name: name
        name: hello
        script:
          command:
          - python
          image: python:3.8
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            import json

            try: name = json.loads(r''''''{{inputs.parameters.name}}'''''')

            except: name = r''''''{{inputs.parameters.name}}''''''


            print(''Hello, {name}!''.format(name=name))'
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: my-dag-input
                value: call-1
            name: call-1
            template: my-dag
          - arguments:
              parameters:
              - name: my-dag-input
                value: call-2
            depends: call-1
            name: call-2
            template: my-dag
        name: calling-dag
    ```

