# Cron Workflow

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/cron-workflow.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, CronWorkflow

    with CronWorkflow(
        name="hello-world",
        entrypoint="hello-world-with-time",
        schedule="* * * * *",
        timezone="America/Los_Angeles",
        starting_deadline_seconds=0,
        concurrency_policy="Replace",
        successful_jobs_history_limit=4,
        failed_jobs_history_limit=4,
        cron_suspend=False,
    ) as w:
        print_message = Container(
            name="hello-world-with-time",
            image="busybox",
            command=["echo"],
            args=["🕓 hello world. Scheduled on: {{workflow.scheduledTime}}"],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: CronWorkflow
    metadata:
      name: hello-world
    spec:
      concurrencyPolicy: Replace
      failedJobsHistoryLimit: 4
      schedule: '* * * * *'
      startingDeadlineSeconds: 0
      successfulJobsHistoryLimit: 4
      suspend: false
      timezone: America/Los_Angeles
      workflowSpec:
        entrypoint: hello-world-with-time
        templates:
        - name: hello-world-with-time
          container:
            image: busybox
            args:
            - "\U0001F553 hello world. Scheduled on: {{workflow.scheduledTime}}"
            command:
            - echo
    ```

