from hera.workflows import Container, CronWorkflow

with CronWorkflow(
    name="sleep-when",
    entrypoint="sleep-busybox",
    schedules=["* * * * *"],
    concurrency_policy="Allow",
    when="{{= cronworkflow.lastScheduledTime == nil || (now() - cronworkflow.lastScheduledTime).Seconds() > 360 }}",
) as w:
    print_message = Container(
        name="sleep-busybox",
        image="busybox",
        command=["sleep"],
        args=["10"],
    )
