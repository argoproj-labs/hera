# New Decorators Basic Script






=== "Hera"

    ```python linenums="1"
    from hera.shared import global_config
    from hera.workflows import Input, Output, WorkflowTemplate

    global_config.experimental_features["decorator_syntax"] = True

    w = WorkflowTemplate(name="my-template")


    class MyInput(Input):
        user: str


    @w.script()
    def hello_world(my_input: MyInput) -> Output:
        output = Output()
        output.result = f"Hello Hera User: {my_input.user}!"
        return output


    # Pass script kwargs (including an alternative public template name) in the decorator
    @w.set_entrypoint
    @w.script(name="goodbye-world", labels={"my-label": "my-value"})
    def goodbye(my_input: MyInput) -> Output:
        output = Output()
        output.result = f"Goodbye Hera User: {my_input.user}!"
        return output
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: WorkflowTemplate
    metadata:
      name: my-template
    spec:
      entrypoint: goodbye-world
      templates:
      - inputs:
          parameters:
          - name: user
        name: hello-world
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.new_decorators_basic_script:hello_world
          command:
          - python
          env:
          - name: hera__script_annotations
            value: ''
          - name: hera__outputs_directory
            value: /tmp/hera-outputs
          - name: hera__script_pydantic_io
            value: ''
          image: python:3.8
          source: '{{inputs.parameters}}'
      - inputs:
          parameters:
          - name: user
        metadata:
          labels:
            my-label: my-value
        name: goodbye-world
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.new_decorators_basic_script:goodbye
          command:
          - python
          env:
          - name: hera__script_annotations
            value: ''
          - name: hera__outputs_directory
            value: /tmp/hera-outputs
          - name: hera__script_pydantic_io
            value: ''
          image: python:3.8
          source: '{{inputs.parameters}}'
    ```

