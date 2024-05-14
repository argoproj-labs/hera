# New Dag Decorator Params






=== "Hera"

    ```python linenums="1"
    from pydantic import BaseModel
    from typing_extensions import Annotated

    from hera.shared import global_config
    from hera.workflows import Input, Output, Parameter, Workflow

    global_config.experimental_features["script_annotations"] = True
    global_config.experimental_features["script_pydantic_io"] = True


    w = Workflow(generate_name="my-workflow-")


    class SetupConfig(BaseModel):
        a_param: str


    class SetupOutput(Output):
        environment_parameter: str
        an_annotated_parameter: Annotated[int, Parameter(name="dummy-param")]  # use an annotated non-str
        setup_config: Annotated[SetupConfig, Parameter(name="setup-config")]  # use a pydantic BaseModel


    @w.script()
    def setup() -> SetupOutput:
        return SetupOutput(
            environment_parameter="linux",
            an_annotated_parameter=42,
            setup_config=SetupConfig(a_param="test"),
            result="Setting things up",
        )


    class ConcatInput(Input):
        word_a: Annotated[str, Parameter(name="word_a", default="")]
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
    @w.dag()
    def worker(worker_input: WorkerInput) -> WorkerOutput:
        setup_task = setup()
        task_a = concat(
            ConcatInput(
                word_a=worker_input.value_a,
                word_b=setup_task.environment_parameter + str(setup_task.an_annotated_parameter),
            )
        )
        task_b = concat(ConcatInput(word_a=worker_input.value_b, word_b=setup_task.result))
        final_task = concat(ConcatInput(word_a=task_a.result, word_b=task_b.result))

        return WorkerOutput(value=final_task.result)
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: my-workflow-
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
          - name: setup-config
            valueFrom:
              path: /tmp/hera-outputs/parameters/setup-config
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.new_dag_decorator_params:setup
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
          - default: ''
            name: word_a
          - name: word_b
        name: concat
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.new_dag_decorator_params:concat
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
          - name: setup_task
            template: setup
          - arguments:
              parameters:
              - name: word_a
                value: '{{inputs.parameters.value_a}}'
              - name: word_b
                value: '{{tasks.setup_task.outputs.parameters.environment_parameter}}{{tasks.setup_task.outputs.parameters.dummy-param}}'
            depends: setup_task
            name: task_a
            template: concat
          - arguments:
              parameters:
              - name: word_a
                value: '{{inputs.parameters.value_b}}'
              - name: word_b
                value: '{{tasks.setup_task.outputs.result}}'
            depends: setup_task
            name: task_b
            template: concat
          - arguments:
              parameters:
              - name: word_a
                value: '{{tasks.task_a.outputs.result}}'
              - name: word_b
                value: '{{tasks.task_b.outputs.result}}'
            depends: task_a && task_b
            name: final_task
            template: concat
        inputs:
          parameters:
          - default: my default
            name: value_a
          - name: value_b
          - default: '42'
            name: an_int_value
        name: worker
        outputs:
          parameters:
          - name: value
            valueFrom:
              parameter: '{{tasks.final_task.outputs.result}}'
    ```

