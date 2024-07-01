# New Decorators Passthrough Io






=== "Hera"

    ```python linenums="1"
    from typing_extensions import Annotated

    from hera.shared import global_config
    from hera.workflows import Artifact, ArtifactLoader, Input, Output, WorkflowTemplate

    global_config.experimental_features["decorator_syntax"] = True

    w = WorkflowTemplate(name="my-template")


    class PassthroughIO(Input, Output):
        my_str: str
        my_int: int
        my_artifact: Annotated[str, Artifact(name="my-artifact", loader=ArtifactLoader.json)]


    @w.script()
    def give_output() -> PassthroughIO:
        return PassthroughIO(my_str="test", my_int=42)


    @w.script()
    def take_input(inputs: PassthroughIO) -> Output:
        return Output(result=f"Got a string: {inputs.my_str}, got an int: {inputs.my_int}")


    @w.dag()
    def my_dag():
        output_task = give_output()
        take_input(output_task)
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: WorkflowTemplate
    metadata:
      name: my-template
    spec:
      templates:
      - name: give-output
        outputs:
          artifacts:
          - name: my-artifact
            path: /tmp/hera-outputs/artifacts/my-artifact
          parameters:
          - name: my_str
            valueFrom:
              path: /tmp/hera-outputs/parameters/my_str
          - name: my_int
            valueFrom:
              path: /tmp/hera-outputs/parameters/my_int
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.new_decorators_passthrough_io:give_output
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
          artifacts:
          - name: my-artifact
            path: /tmp/hera-inputs/artifacts/my-artifact
          parameters:
          - name: my_str
          - name: my_int
        name: take-input
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.new_decorators_passthrough_io:take_input
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
      - dag:
          tasks:
          - name: output_task
            template: give-output
          - arguments:
              artifacts:
              - from: '{{tasks.output_task.outputs.artifacts.my-artifact}}'
                name: my-artifact
              parameters:
              - name: my_str
                value: '{{tasks.output_task.outputs.parameters.my_str}}'
              - name: my_int
                value: '{{tasks.output_task.outputs.parameters.my_int}}'
            depends: output_task
            name: take-input
            template: take-input
        name: my-dag
    ```

