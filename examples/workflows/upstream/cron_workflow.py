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
