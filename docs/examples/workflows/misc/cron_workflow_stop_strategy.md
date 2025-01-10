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
            image="docker/whalesay:latest",
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
      schedules:
      - '*/3 * * * *'
      - '*/2 * * * *'
      startingDeadlineSeconds: 0
      stopStrategy:
        expression: cronworkflow.failed >= 3
      successfulJobsHistoryLimit: 4
      suspend: false
      timezone: America/Los_Angeles
      workflowSpec:
        entrypoint: whalesay
        templates:
        - container:
            args:
            - "\U0001F553 hello world. Scheduled on: {{workflow.scheduledTime}}"
            command:
            - cowsay
            image: docker/whalesay:latest
          name: whalesay
    ```

