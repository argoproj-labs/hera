# New Steps Decorator With Parallel Steps



This example shows the use of the new `steps` decorator, including parallel steps.


=== "Hera"

    ```python linenums="1"
    from typing import Annotated

    from hera.shared import global_config
    from hera.workflows import Input, Output, Parameter, Workflow, parallel

    global_config.experimental_features["decorator_syntax"] = True


    w = Workflow(
        generate_name="steps-",
        arguments={"value_b": "a value for b!"},
    )


    class SetupOutput(Output):
        environment_parameter: str
        an_annotated_parameter: Annotated[int, Parameter(name="dummy-param")]


    @w.script()
    def setup() -> SetupOutput:
        return SetupOutput(environment_parameter="linux", an_annotated_parameter=42, result="Setting things up")


    class ConcatInput(Input):
        word_a: Annotated[str, Parameter(name="word_a")] = ""
        word_b: str


    @w.script()
    def concat(concat_input: ConcatInput) -> Output:
        return Output(result=f"{concat_input.word_a} {concat_input.word_b}")


    class WorkerInput(Input):
        value_a: str = "my default"
        value_b: str
        an_int_value: int = 42


    class WorkerOutput(Output):
        value: str


    @w.set_entrypoint
    @w.steps()
    def worker(worker_input: WorkerInput) -> WorkerOutput:
        setup_step = setup()
        with parallel():
            step_a = concat(
                ConcatInput(
                    word_a=worker_input.value_a,
                    word_b=setup_step.environment_parameter + str(setup_step.an_annotated_parameter),
                )
            )
            step_b = concat(ConcatInput(word_a=worker_input.value_b, word_b=setup_step.result))

        final_step = concat(ConcatInput(word_a=step_a.result, word_b=step_b.result))

        return WorkerOutput(value=final_step.result)
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: steps-
    spec:
      entrypoint: worker
      templates:
      - name: setup
        outputs:
          parameters:
          - name: environment_parameter
            valueFrom:
              path: /tmp/hera-outputs/parameters/environment_parameter
          - name: dummy-param
            valueFrom:
              path: /tmp/hera-outputs/parameters/dummy-param
        script:
          image: python:3.10
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.new_steps_decorator_with_parallel_steps:setup
          command:
          - python
          env:
          - name: hera__outputs_directory
            value: /tmp/hera-outputs
      - name: concat
        inputs:
          parameters:
          - name: word_a
            default: ''
          - name: word_b
        script:
          image: python:3.10
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.new_steps_decorator_with_parallel_steps:concat
          command:
          - python
          env:
          - name: hera__outputs_directory
            value: /tmp/hera-outputs
      - name: worker
        steps:
        - - name: setup-step
            template: setup
        - - name: step-a
            template: concat
            arguments:
              parameters:
              - name: word_a
                value: '{{inputs.parameters.value_a}}'
              - name: word_b
                value: '{{steps.setup-step.outputs.parameters.environment_parameter}}{{steps.setup-step.outputs.parameters.dummy-param}}'
          - name: step-b
            template: concat
            arguments:
              parameters:
              - name: word_a
                value: '{{inputs.parameters.value_b}}'
              - name: word_b
                value: '{{steps.setup-step.outputs.result}}'
        - - name: final-step
            template: concat
            arguments:
              parameters:
              - name: word_a
                value: '{{steps.step-a.outputs.result}}'
              - name: word_b
                value: '{{steps.step-b.outputs.result}}'
        inputs:
          parameters:
          - name: value_a
            default: my default
          - name: value_b
          - name: an_int_value
            default: '42'
        outputs:
          parameters:
          - name: value
            valueFrom:
              parameter: '{{steps.final-step.outputs.result}}'
      arguments:
        parameters:
        - name: value_b
          value: a value for b!
    ```

