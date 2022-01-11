"""This example showcases how to structure a linear chain of tasks"""
from hera.task import Task
from hera.workflow import Workflow
from hera.workflow_service import WorkflowService


def task_1():
    print('Performed task 1!')


def task_2():
    print('Performed task 2!')


def task_3():
    print('Performed task 3!')


def task_4():
    print('Performed task 4')


# TODO: replace the domain and token with your own
ws = WorkflowService(host='my-argo-server.com', token='my-auth-token')
w = Workflow('linear', ws)
t1 = Task('t1', task_1)
t2 = Task('t2', task_2)
t3 = Task('t3', task_3)
t4 = Task('t4', task_4)

t1 >> t2 >> t3 >> t4  # t1.next(t2).next(t3).next(t4)

w.add_tasks(t1, t2, t3, t4)
w.submit()
