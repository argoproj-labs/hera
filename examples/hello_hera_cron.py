"""This example showcases the cron hello world example of Hera"""

from hera import CronWorkflow, CronWorkflowService, Task


def hello():
    print('Hello, Hera!')


with CronWorkflow(
    'hello-hera-cron',
    "5 4 * * *",
    service=CronWorkflowService(host='https://my-argo-server.com', token='my-auth-token'),
    timezone="UTC",
) as cw:
    Task('t', hello)

cw.create()
