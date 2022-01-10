"""
This example showcases how to set a retry on a task. The retry will make the task back off for 5 seconds
post-failure and allow the retries to occur over a duration of 60 seconds.
"""
from hera.v1.retry import Retry
from hera.v1.task import Task
from hera.v1.workflow import Workflow
from hera.v1.workflow_service import WorkflowService


def random_fail():
    import random

    p = random.random()
    if p < 0.5:
        raise Exception('p < .5 = FAIL')
    print('p >= .5 = SUCCESS')


# TODO: replace the domain and token with your own
ws = WorkflowService('my-argo-server.com', 'my-auth-token')
w = Workflow('retry', ws)
t = Task('fail', random_fail, retry=Retry(duration=3, max_duration=9))
w.add_task(t)
w.submit()
