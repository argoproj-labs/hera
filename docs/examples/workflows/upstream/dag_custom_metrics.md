# Dag Custom Metrics

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-custom-metrics.yaml).




=== "Hera"

    ```python linenums="1"
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
                name="TEST-ONE",
                arguments=[
                    Parameter(name="message", value="console output-->TEST-{{item.command}}"),
                    Parameter(name="tag", value="{{item.tag}}"),
                ],
                with_items=[
                    {"tag": "TEST-ONE-A", "command": "ONE-A"},
                    {"tag": "TEST-ONE-B", "command": "ONE-B"},
                ],
            )
            echo(
                name="TEST-TWO",
                arguments=[
                    Parameter(name="message", value="console output-->TEST-{{item.command}}"),
                    Parameter(name="tag", value="{{item.tag}}"),
                ],
                with_items=[
                    {"tag": "TEST-TWO-A", "command": "TWO-A"},
                    {"tag": "TEST-TWO-B", "command": "TWO-B"},
                ],
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dag-task-
    spec:
      entrypoint: dag-task
      templates:
      - name: dag-task
        dag:
          tasks:
          - name: TEST-ONE
            template: echo
            withItems:
            - command: ONE-A
              tag: TEST-ONE-A
            - command: ONE-B
              tag: TEST-ONE-B
            arguments:
              parameters:
              - name: message
                value: console output-->TEST-{{item.command}}
              - name: tag
                value: '{{item.tag}}'
          - name: TEST-TWO
            template: echo
            withItems:
            - command: TWO-A
              tag: TEST-TWO-A
            - command: TWO-B
              tag: TEST-TWO-B
            arguments:
              parameters:
              - name: message
                value: console output-->TEST-{{item.command}}
              - name: tag
                value: '{{item.tag}}'
      - name: echo
        container:
          image: alpine:3.7
          command:
          - echo
          - '{{inputs.parameters.message}}'
        inputs:
          parameters:
          - name: message
          - name: tag
        metrics:
          prometheus:
          - name: playground_workflow_duration_task_seconds
            help: Duration gauge by task name in seconds - task level
            labels:
            - key: playground_task_name
              value: '{{inputs.parameters.tag}}'
            - key: status
              value: '{{status}}'
            gauge:
              realtime: false
              value: '{{duration}}'
          - name: playground_workflow_result_task_counter
            help: Count of task execution by result status  - task level
            labels:
            - key: playground_task_name_counter
              value: '{{inputs.parameters.tag}}'
            - key: status
              value: '{{status}}'
            counter:
              value: '1'
      metrics:
        prometheus:
        - name: playground_workflow_duration
          help: Duration gauge by workflow level
          labels:
          - key: playground_id_workflow
            value: test
          - key: status
            value: '{{workflow.status}}'
          gauge:
            realtime: false
            value: '{{workflow.duration}}'
        - name: playground_workflow_result_counter
          help: Count of workflow execution by result status  - workflow level
          labels:
          - key: playground_id_workflow_counter
            value: test
          - key: status
            value: '{{workflow.status}}'
          counter:
            value: '1'
    ```

