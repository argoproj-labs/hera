"""This example showcases the hello world example of Hera"""
from hera import Task, Workflow, WorkflowService


def hello():
    print('Hello, Hera!')


with Workflow('hello-hera', service=WorkflowService(host='https://my-argo-server.com', token='my-auth-token')) as w:
    Task('t', hello)

w.create()
