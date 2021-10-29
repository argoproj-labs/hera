"""This example showcases the hello world example of Hera"""
from hera.v1.task import Task
from hera.v1.workflow import Workflow
from hera.v1.workflow_service import WorkflowService


def hello():
    print('Hello, Hera!')


# TODO: replace the domain and token with your own
ws = WorkflowService('my-argo-server.com', 'my-auth-token')
w = Workflow('hello-hera', ws)
t = Task('t', hello)
w.add_task(t)
w.submit()
