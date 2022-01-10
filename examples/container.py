"""This example showcases how to run a container, rather than a Python, function, as the payload of a task in Hera"""
from hera.v1.task import Task
from hera.v1.workflow import Workflow
from hera.v1.workflow_service import WorkflowService

# TODO: replace the domain and token with your own
ws = WorkflowService('my-argo-server.com', 'my-auth-token')
w = Workflow('container', ws)

# notice the placeholder `lambda: None`, for now this is required because
# func is a required parameter, by design. Perhaps this can be made
# `Optional[Callable]` in the future
t = Task('cowsay', lambda: None, image='docker/whalesay', command=['cowsay', 'foo'])
w.add_task(t)
w.submit()
