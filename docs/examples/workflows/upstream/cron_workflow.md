# Cron Workflow

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/cron-workflow.yaml).



## Hera

```python
from hera.workflows import Container, CronWorkflow

with CronWorkflow(
    name="hello-world",
    entrypoint="whalesay",
    schedule="* * * * *",
    timezone="America/Los_Angeles",
    starting_deadline_seconds=0,
    concurrency_policy="Replace",
    successful_jobs_history_limit=4,
    failed_jobs_history_limit=4,
    cron_suspend=False,
) as w:
    whalesay = Container(
        name="whalesay",
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=["🕓 hello world. Scheduled on: {{workflow.scheduledTime}}"],
    )
```

## YAML

```yaml
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
