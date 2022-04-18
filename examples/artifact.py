"""This example showcases a simple artifact passing mechanism between two tasks.

The first task, t1, creates a file located at `/file` containing a message. The second
task, t2, takes this artifact, places it at its own `/file` path, and print out the content.
"""

from hera.artifact import InputArtifact, OutputArtifact
from hera.task import Task
from hera.workflow import Workflow
from hera.workflow_service import WorkflowService


def writer():
    with open('/file', 'w+') as f:
        f.write('Hello, world!')


def consumer():
    with open('/file', 'r') as f:
        print(f.readlines())  # prints `Hello, world!` to `stdout`


# TODO: replace the domain and token with your own
ws = WorkflowService(host='https://my-argo-server.com', token='my-auth-token')
w = Workflow('artifact', ws)
w_t = Task('writer', writer, output_artifacts=[OutputArtifact(name='test', path='/file')])
c_t = Task(
    'consumer',
    consumer,
    input_artifacts=[InputArtifact(name='test', path='/file', from_task='writer', artifact_name='test')],
)

w_t >> c_t
w.add_tasks(w_t, c_t)
w.create()
