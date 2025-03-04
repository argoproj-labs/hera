# Cron When

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/cron-when.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, CronWorkflow

    with CronWorkflow(
        name="sleep-when",
        entrypoint="sleep-busybox",
        schedule="* * * * *",
        concurrency_policy="Allow",
        when="{{= cronworkflow.lastScheduledTime == nil || (now() - cronworkflow.lastScheduledTime).Seconds() > 360 }}",
    ) as w:
        print_message = Container(
            name="sleep-busybox",
            image="busybox",
            command=["sleep"],
            args=["10"],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: CronWorkflow
    metadata:
      name: sleep-when
    spec:
      concurrencyPolicy: Allow
      schedule: '* * * * *'
      when: '{{= cronworkflow.lastScheduledTime == nil || (now() - cronworkflow.lastScheduledTime).Seconds()
        > 360 }}'
      workflowSpec:
        entrypoint: sleep-busybox
        templates:
        - name: sleep-busybox
          container:
            image: busybox
            args:
            - '10'
            command:
            - sleep
    ```

