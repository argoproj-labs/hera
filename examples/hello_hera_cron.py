"""This example showcases the cron hello world example of Hera"""
from hera.cron_workflow import CronWorkflow
from hera.cron_workflow_service import CronWorkflowService
from hera.task import Task


def hello():
    print('Hello, Hera!')


# TODO: replace the domain and token with your own
cws = CronWorkflowService(host='https://my-argo-server.com', token='my-auth-token')
cw = CronWorkflow('hello-hera-cron', "5 4 * * *", cws, timezone="UTC")
t = Task('t', hello)
cw.add_task(t)
cw.create()
