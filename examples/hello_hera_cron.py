"""This example showcases the cron hello world example of Hera"""

from hera import CronWorkflow, Task, WorkflowService


def hello():
    print("Hello, Hera!")


with CronWorkflow(
    "hello-hera-cron",
    "5 4 * * *",
    service=WorkflowService(host="https://my-argo-server.com", token="my-auth-token"),
    timezone="UTC",
) as cw:
    Task("t", hello)

cw.create()

# Delete the cron workflow:
# cw.delete()

# Update the cron workflow after redefining it, but keeping the same name:
# cw.update()
