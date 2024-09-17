# Callable Steps






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Parameter, Steps, Workflow, script


    @script()
    def hello(name: str):
        print("Hello, {name}!".format(name=name))


    with Workflow(
        generate_name="callable-steps-",
        entrypoint="calling-steps",
    ) as w:
        with Steps(name="my-steps", inputs=Parameter(name="my-step-input")) as my_steps:
            hello(name="hello-1", arguments={"name": "hello-1-{{inputs.parameters.my-step-input}}"})
            hello(name="hello-2", arguments={"name": "hello-2-{{inputs.parameters.my-step-input}}"})

        with Steps(name="calling-steps") as s:
            my_steps(name="call-1", arguments={"my-step-input": "call-1"})
            my_steps(name="call-2", arguments={"my-step-input": "call-2"})
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: callable-steps-
    spec:
      entrypoint: calling-steps
      templates:
      - inputs:
          parameters:
          - name: my-step-input
        name: my-steps
        steps:
        - - arguments:
              parameters:
              - name: name
                value: hello-1-{{inputs.parameters.my-step-input}}
            name: hello-1
            template: hello
        - - arguments:
              parameters:
              - name: name
                value: hello-2-{{inputs.parameters.my-step-input}}
            name: hello-2
            template: hello
      - inputs:
          parameters:
          - name: name
        name: hello
        script:
          command:
          - python
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: name = json.loads(r'''{{inputs.parameters.name}}''')
            except: name = r'''{{inputs.parameters.name}}'''

            print('Hello, {name}!'.format(name=name))
      - name: calling-steps
        steps:
        - - arguments:
              parameters:
              - name: my-step-input
                value: call-1
            name: call-1
            template: my-steps
        - - arguments:
              parameters:
              - name: my-step-input
                value: call-2
            name: call-2
            template: my-steps
    ```

