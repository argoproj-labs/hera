# Inner Steps



This example shows how to use a Steps template within another Steps template.

Note, this is different from parallel steps, as parallel steps are a collection of substeps to run in parallel, whereas
this inner steps example shows the use of a whole `Steps` template (which will run sequentially in this example).


=== "Hera"

    ```python linenums="1"
    from hera.workflows import Parameter, Steps, Workflow, script


    @script()
    def hello(name: str):
        print("Hello, {name}!".format(name=name))


    with Workflow(
        generate_name="callable-inner-steps-",
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
      generateName: callable-inner-steps-
    spec:
      entrypoint: calling-steps
      templates:
      - name: my-steps
        steps:
        - - name: hello-1
            template: hello
            arguments:
              parameters:
              - name: name
                value: hello-1-{{inputs.parameters.my-step-input}}
        - - name: hello-2
            template: hello
            arguments:
              parameters:
              - name: name
                value: hello-2-{{inputs.parameters.my-step-input}}
        inputs:
          parameters:
          - name: my-step-input
      - name: hello
        inputs:
          parameters:
          - name: name
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: name = json.loads(r'''{{inputs.parameters.name}}''')
            except: name = r'''{{inputs.parameters.name}}'''

            print('Hello, {name}!'.format(name=name))
          command:
          - python
      - name: calling-steps
        steps:
        - - name: call-1
            template: my-steps
            arguments:
              parameters:
              - name: my-step-input
                value: call-1
        - - name: call-2
            template: my-steps
            arguments:
              parameters:
              - name: my-step-input
                value: call-2
    ```

