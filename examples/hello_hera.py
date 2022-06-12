"""This example showcases the hello world example of Hera"""
from hera import Task, Workflow, WorkflowService


def hello():
    print('Hello, Hera!')


# TODO: replace the domain and token with your own
ws = WorkflowService(host='https://my-argo-server.com', token='my-auth-token')
w = Workflow('hello-hera', ws)
t = Task('t', hello)
w.add_task(t)
w.create()
