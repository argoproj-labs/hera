"""This example showcases the cron hello world example of Hera"""
from hera.v1.task import Task
from hera.v1.cron_workflow import CronWorkflow
from hera.v1.cron_workflow_service import CronWorkflowService


def hello():
    print('Hello, Hera!')


# TODO: replace the domain and token with your own
cws = CronWorkflowService('my-argo-server.com', 'my-auth-token')
cw = CronWorkflow('hello-hera', "5 4 * * *", cws)
t = Task('t', hello)
cw.add_task(t)
cw.create()
