"""This example showcases how to run a container, rather than a Python, function, as the payload of a task in Hera"""
from hera import Task, Workflow, WorkflowService

with Workflow('container', service=WorkflowService(host='https://my-argo-server.com', token='my-auth-token')) as w:
    Task('cowsay', image='docker/whalesay', command=['cowsay', 'foo'])

w.create()
