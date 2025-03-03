# New Dag Decorator Params






=== "Hera"

    ```python linenums="1"
    from pydantic import BaseModel
    from typing_extensions import Annotated

    from hera.shared import global_config
    from hera.workflows import Input, Output, Parameter, Workflow

    global_config.experimental_features["decorator_syntax"] = True


    w = Workflow(generate_name="my-workflow-")


    class SetupConfig(BaseModel):
        a_param: str


    class SetupOutput(Output):
        environment_parameter: str
        an_annotated_parameter: Annotated[int, Parameter()]  # use an annotated non-str, infer name from field
        setup_config: Annotated[SetupConfig, Parameter(name="setup-config")]  # use a pydantic BaseModel


    @w.script()
    def setup() -> SetupOutput:
        return SetupOutput(
            environment_parameter="linux",
            an_annotated_parameter=42,
            setup_config=SetupConfig(a_param="test"),
            result="Setting things up",
        )


    class ConcatConfig(BaseModel):
        reverse: bool


    class ConcatInput(Input):
        word_a: Annotated[str, Parameter(name="word_a")] = ""
        word_b: str
        concat_config: ConcatConfig = ConcatConfig(reverse=False)


    @w.script()
    def concat(concat_input: ConcatInput) -> Output:
        res = f"{concat_input.word_a} {concat_input.word_b}"
        if concat_input.reverse:
            res = res[::-1]
        return Output(result=res)


    class WorkerConfig(BaseModel):
        param_1: str
        param_2: str


    class WorkerInput(Input):
        value_a: str = "my default"
        value_b: str
        an_int_value: int = 42
        a_basemodel: WorkerConfig = WorkerConfig(param_1="Hello", param_2="world")


    class WorkerOutput(Output):
        result_value: str
        another_value: str


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

        return WorkerOutput(result_value=final_task.result, another_value=setup_task.an_annotated_parameter)
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
          - name: an_annotated_parameter
            valueFrom:
              path: /tmp/hera-outputs/parameters/an_annotated_parameter
          - name: setup-config
            valueFrom:
              path: /tmp/hera-outputs/parameters/setup-config
        script:
          image: python:3.9
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.new_dag_decorator_params:setup
          command:
          - python
          env:
          - name: hera__outputs_directory
            value: /tmp/hera-outputs
          - name: hera__script_pydantic_io
            value: ''
      - name: concat
        inputs:
          parameters:
          - name: word_a
            default: ''
          - name: word_b
          - name: concat_config
            default: '{"reverse": false}'
        script:
          image: python:3.9
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.new_dag_decorator_params:concat
          command:
          - python
          env:
          - name: hera__outputs_directory
            value: /tmp/hera-outputs
          - name: hera__script_pydantic_io
            value: ''
      - name: worker
        dag:
          tasks:
          - name: setup-task
            template: setup
          - name: task-a
            depends: setup-task
            template: concat
            arguments:
              parameters:
              - name: word_a
                value: '{{inputs.parameters.value_a}}'
              - name: word_b
                value: '{{tasks.setup-task.outputs.parameters.environment_parameter}}{{tasks.setup-task.outputs.parameters.an_annotated_parameter}}'
              - name: concat_config
                value: '{"reverse": false}'
          - name: task-b
            depends: setup-task
            template: concat
            arguments:
              parameters:
              - name: word_a
                value: '{{inputs.parameters.value_b}}'
              - name: word_b
                value: '{{tasks.setup-task.outputs.result}}'
              - name: concat_config
                value: '{"reverse": false}'
          - name: final-task
            depends: task-a && task-b
            template: concat
            arguments:
              parameters:
              - name: word_a
                value: '{{tasks.task-a.outputs.result}}'
              - name: word_b
                value: '{{tasks.task-b.outputs.result}}'
              - name: concat_config
                value: '{"reverse": false}'
        inputs:
          parameters:
          - name: value_a
            default: my default
          - name: value_b
          - name: an_int_value
            default: '42'
          - name: a_basemodel
            default: '{"param_1": "Hello", "param_2": "world"}'
        outputs:
          parameters:
          - name: result_value
            valueFrom:
              parameter: '{{tasks.final-task.outputs.result}}'
          - name: another_value
            valueFrom:
              parameter: '{{tasks.setup-task.outputs.parameters.an_annotated_parameter}}'
    ```

