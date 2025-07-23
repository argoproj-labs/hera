from hera.workflows import Container, CronWorkflow

with CronWorkflow(
    name="hello-world",
    entrypoint="hello-world-with-time",
    schedules=["* * * * *"],
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
