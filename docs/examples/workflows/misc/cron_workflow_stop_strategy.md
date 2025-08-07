# Cron Workflow Stop Strategy






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, CronWorkflow
    from hera.workflows.models import StopStrategy

    with CronWorkflow(
        name="hello-world-multiple-schedules",
        entrypoint="whalesay",
        schedules=[
            "*/3 * * * *",
            "*/2 * * * *",
        ],
        stop_strategy=StopStrategy(expression="cronworkflow.failed >= 3"),
        timezone="America/Los_Angeles",
        starting_deadline_seconds=0,
        concurrency_policy="Replace",
        successful_jobs_history_limit=4,
        failed_jobs_history_limit=4,
        cron_suspend=False,
    ) as w:
        Container(
            name="whalesay",
            image="argoproj/argosay:v2",
            command=["cowsay"],
            args=["🕓 hello world. Scheduled on: {{workflow.scheduledTime}}"],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: CronWorkflow
    metadata:
      name: hello-world-multiple-schedules
    spec:
      concurrencyPolicy: Replace
      failedJobsHistoryLimit: 4
      startingDeadlineSeconds: 0
      successfulJobsHistoryLimit: 4
      suspend: false
      timezone: America/Los_Angeles
      schedules:
      - '*/3 * * * *'
      - '*/2 * * * *'
      stopStrategy:
        expression: cronworkflow.failed >= 3
      workflowSpec:
        entrypoint: whalesay
        templates:
        - name: whalesay
          container:
            image: argoproj/argosay:v2
            args:
            - "\U0001F553 hello world. Scheduled on: {{workflow.scheduledTime}}"
            command:
            - cowsay
    ```

