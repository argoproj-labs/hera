from hera.workflows import (
    DAG,
    Container,
    Counter,
    Gauge,
    Label,
    Parameter,
    Workflow,
)

echo = Container(
    name="echo",
    image="alpine:3.7",
    command=["echo", "{{inputs.parameters.message}}"],
    inputs=[Parameter(name="message"), Parameter(name="tag")],
    metrics=[
        Gauge(
            name="playground_workflow_duration_task_seconds",
            help="Duration gauge by task name in seconds - task level",
            labels=[
                Label(key="playground_task_name", value="{{inputs.parameters.tag}}"),
                Label(key="status", value="{{status}}"),
            ],
            realtime=False,
            value="{{duration}}",
        ),
        Counter(
            name="playground_workflow_result_task_counter",
            help="Count of task execution by result status  - task level",
            labels=[
                Label(key="playground_task_name_counter", value="{{inputs.parameters.tag}}"),
                Label(key="status", value="{{status}}"),
            ],
            value="1",
        ),
    ],
    use_func_params_in_call=True,
)

with Workflow(
    generate_name="dag-task-",
    entrypoint="dag-task",
    metrics=[
        Gauge(
            name="playground_workflow_duration",
            labels=[
                Label(key="playground_id_workflow", value="test"),
                Label(key="status", value="{{workflow.status}}"),
            ],
            realtime=False,
            value="{{workflow.duration}}",
            help="Duration gauge by workflow level",
        ),
        Counter(
            name="playground_workflow_result_counter",
            labels=[
                Label(key="playground_id_workflow_counter", value="test"),
                Label(key="status", value="{{workflow.status}}"),
            ],
            value="1",
            help="Count of workflow execution by result status  - workflow level",
        ),
    ],
) as w:
    with DAG(name="dag-task"):
        echo(
            Parameter(name="message", value="console output-->TEST-{{item.command}}"),
            Parameter(name="tag", value="{{item.tag}}"),
        ).with_(
            name="TEST-ONE",
            with_items=[
                {"tag": "TEST-ONE-A", "command": "ONE-A"},
                {"tag": "TEST-ONE-B", "command": "ONE-B"},
            ],
        )
        echo(
            Parameter(name="message", value="console output-->TEST-{{item.command}}"),
            Parameter(name="tag", value="{{item.tag}}"),
        ).with_(
            name="TEST-TWO",
            with_items=[
                {"tag": "TEST-TWO-A", "command": "TWO-A"},
                {"tag": "TEST-TWO-B", "command": "TWO-B"},
            ],
        )
