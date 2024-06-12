# New Decorators Auto Template Refs






=== "Hera"

    ```python linenums="1"
    from pydantic import BaseModel
    from typing_extensions import Annotated

    from hera.shared import global_config
    from hera.workflows import ClusterWorkflowTemplate, Input, Output, Parameter, Workflow, WorkflowTemplate

    global_config.experimental_features["decorator_syntax"] = True


    # Here we are going to define a Workflow that uses templates from external WorkflowTemplates
    w = Workflow(generate_name="my-workflow-")

    wt = WorkflowTemplate(name="my-workflow-template")
    cwt = ClusterWorkflowTemplate(name="my-cluster-workflow-template")


    class SetupConfig(BaseModel):
        a_param: str


    class SetupOutput(Output):
        environment_parameter: str
        an_annotated_parameter: Annotated[int, Parameter(name="dummy-param")]  # use an annotated non-str
        setup_config: Annotated[SetupConfig, Parameter(name="setup-config")]  # use a pydantic BaseModel


    # External templates can have the actual implementation
    @cwt.script()
    def setup() -> SetupOutput:
        return SetupOutput(
            environment_parameter="linux",
            an_annotated_parameter=42,
            setup_config=SetupConfig(a_param="test"),
            result="Setting things up",
        )


    # Or be stubbed out
    @cwt.dag()
    def run_setup_dag() -> Output: ...


    class ConcatConfig(BaseModel):
        reverse: bool


    class ConcatInput(Input):
        word_a: Annotated[str, Parameter(name="word_a", default="")]
        word_b: str
        concat_config: ConcatConfig = ConcatConfig(reverse=False)


    @wt.script()
    def concat(concat_input: ConcatInput) -> Output: ...


    class WorkerConfig(BaseModel):
        param_1: str
        param_2: str


    class WorkerInput(Input):
        value_a: str = "my default"
        value_b: str
        an_int_value: int = 42
        a_basemodel: WorkerConfig = WorkerConfig(param_1="Hello", param_2="world")


    class WorkerOutput(Output):
        value: str


    @w.set_entrypoint
    @w.dag()
    def worker(worker_input: WorkerInput) -> WorkerOutput:
        # We can call functions belonging to other WorkflowTemplates in this Workflow's DAG.
        # Hera will resolve the reference into a TemplateRef used in the Task.
        run_setup_dag()  # Comes from the ClusterWorkflowTemplate and is stubbed
        setup_task = setup()  # Comes from the ClusterWorkflowTemplate with implementation details (but are not used)
        task_a = concat(  # Comes from the WorkflowTemplate and is stubbed
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
      - dag:
          tasks:
          - name: run-setup-dag
            templateRef:
              clusterScope: true
              name: my-cluster-workflow-template
              template: run-setup-dag
          - name: setup_task
            templateRef:
              clusterScope: true
              name: my-cluster-workflow-template
              template: setup
          - arguments:
              parameters:
              - name: word_a
                value: '{{inputs.parameters.value_a}}'
              - name: word_b
                value: '{{tasks.setup_task.outputs.parameters.environment_parameter}}{{tasks.setup_task.outputs.parameters.dummy-param}}'
              - name: concat_config
                value: '{"reverse": false}'
            depends: setup_task
            name: task_a
            templateRef:
              name: my-workflow-template
              template: concat
          - arguments:
              parameters:
              - name: word_a
                value: '{{inputs.parameters.value_b}}'
              - name: word_b
                value: '{{tasks.setup_task.outputs.result}}'
              - name: concat_config
                value: '{"reverse": false}'
            depends: setup_task
            name: task_b
            templateRef:
              name: my-workflow-template
              template: concat
          - arguments:
              parameters:
              - name: word_a
                value: '{{tasks.task_a.outputs.result}}'
              - name: word_b
                value: '{{tasks.task_b.outputs.result}}'
              - name: concat_config
                value: '{"reverse": false}'
            depends: task_a && task_b
            name: final_task
            templateRef:
              name: my-workflow-template
              template: concat
        inputs:
          parameters:
          - default: my default
            name: value_a
          - name: value_b
          - default: '42'
            name: an_int_value
          - default: '{"param_1": "Hello", "param_2": "world"}'
            name: a_basemodel
        name: worker
        outputs:
          parameters:
          - name: value
            valueFrom:
              parameter: '{{tasks.final_task.outputs.result}}'
    ```

