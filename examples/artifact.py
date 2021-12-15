"""This example showcases a simple artifact passing mechanism between two tasks.

The first task, t1, creates a file located at `/file` containing a message. The second
task, t2, takes this artifact, places it at its own `/file` path, and print out the content.
"""
from hera.v1.artifact import InputArtifact, OutputArtifact
from hera.v1.task import Task
from hera.v1.workflow import Workflow
from hera.v1.workflow_service import WorkflowService


def writer():
    with open('/file', 'w+') as f:
        f.write('Hello, world!')


def consumer():
    with open('/file', 'r') as f:
        print(f.readlines())  # prints `Hello, world!` to `stdout`


# TODO: replace the domain and token with your own
ws = WorkflowService('my-argo-server.com', 'my-auth-token')
w = Workflow('artifact-passing', ws)
w_t = Task('writer', writer, output_artifacts=[OutputArtifact(name='test', path='/file')])
c_t = Task(
    'consumer',
    consumer,
    input_artifacts=[InputArtifact(name='test', path='/file', from_task='writer', artifact_name='test')],
)

w_t >> c_t
w.add_tasks(w_t, c_t)
w.submit()
