"""This example showcases how to structure a linear chain of tasks"""
from hera import Task, Workflow, WorkflowService


def task_1():
    print('Performed task 1!')


def task_2():
    print('Performed task 2!')


def task_3():
    print('Performed task 3!')


def task_4():
    print('Performed task 4')


# TODO: replace the domain and token with your own
with Workflow('linear', service=WorkflowService(host='my-argo-server.com', token='my-auth-token')) as w:
    (Task('t1', task_1) >> Task('t2', task_2) >> Task('t3', task_3) >> Task('t4', task_4))

w.create()
