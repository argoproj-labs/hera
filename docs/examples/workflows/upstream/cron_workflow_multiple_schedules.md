# Cron Workflow Multiple Schedules

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/cron-workflow-multiple-schedules.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, CronWorkflow

    with CronWorkflow(
        name="hello-world-multiple-schedules",
        entrypoint="whalesay",
        schedules=[
            "*/3 * * * *",
            "*/2 * * * *",
        ],
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
      startingDeadlineSeconds: 0
      successfulJobsHistoryLimit: 4
      suspend: false
      timezone: America/Los_Angeles
      schedules:
      - '*/3 * * * *'
      - '*/2 * * * *'
      workflowSpec:
        entrypoint: whalesay
        templates:
        - name: whalesay
          container:
            image: docker/whalesay:latest
            args:
            - "\U0001F553 hello world. Scheduled on: {{workflow.scheduledTime}}"
            command:
            - cowsay
    ```

