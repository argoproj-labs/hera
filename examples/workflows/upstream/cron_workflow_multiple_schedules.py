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
