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
