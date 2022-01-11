"""This example showcases how to run a container, rather than a Python, function, as the payload of a task in Hera"""
from hera.task import Task
from hera.workflow import Workflow
from hera.workflow_service import WorkflowService

# TODO: replace the domain and token with your own
ws = WorkflowService(host='https://my-argo-server.com', token='my-auth-token')
w = Workflow('fv-testing', ws)

# notice the placeholder `lambda: _`, for now this is required because
# func is a required parameter, by design. Perhaps this can be made
# `Optional[Callable]` in the future
t = Task('cowsay', lambda: _, image='docker/whalesay', command=['cowsay', 'foo'])
w.add_task(t)
w.submit()
