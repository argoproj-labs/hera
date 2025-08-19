"""This example shows a minimal `CronWorkflow`, based on the [Hello World example](hello_world.md)."""

from hera.workflows import CronWorkflow, script


@script()
def hello(s: str):
    print("Hello, {s}!".format(s=s))


with CronWorkflow(
    name="hello-world-cron",
    entrypoint="hello",
    arguments={"s": "world"},
    schedules=[
        "*/2 * * * *",  # Run every 2 minutes
    ],
) as w:
    hello()
