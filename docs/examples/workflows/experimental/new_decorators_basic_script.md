# New Decorators Basic Script



This example shows a simple "hello world" script using the new decorators.

It uses a single input argument, which is passed through the `Workflow`. It also
uses a plain `Output` - by setting the `result` value, it will be printed to stdout
and be available to subsequent tasks (if it were in a DAG).


=== "Hera"

    ```python linenums="1"
    from hera.shared import global_config
    from hera.workflows import Input, Output, Workflow

    global_config.experimental_features["decorator_syntax"] = True

    w = Workflow(name="hello-world", arguments={"user": "me"})


    class MyInput(Input):
        user: str


    @w.set_entrypoint
    @w.script()
    def hello_world(my_input: MyInput) -> Output:
        output = Output()
        output.result = f"Hello Hera User: {my_input.user}!"
        return output
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      name: hello-world
    spec:
      entrypoint: hello-world
      templates:
      - name: hello-world
        inputs:
          parameters:
          - name: user
        script:
          image: python:3.9
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.new_decorators_basic_script:hello_world
          command:
          - python
          env:
          - name: hera__outputs_directory
            value: /tmp/hera-outputs
          - name: hera__script_pydantic_io
            value: ''
      arguments:
        parameters:
        - name: user
          value: me
    ```

