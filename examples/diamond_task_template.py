"""
This example showcases the classic diamond workflow that is used as an example by Argo documentation and
other libraries but with the use of TaskTemplate.

TaskTemplate provides the same functionality as Task with the exception that one TaskTemplate could generate
other tasks that would have their definition stated once and just invoked with arguments.

This makes the workflow size smaller by reusing task templates in tasks. Also, it improves consistency and
allows specifying default values for tasks.
"""
from hera.task_template import TaskTemplate
from hera.workflow import Workflow
from hera.workflow_service import WorkflowService


def say(message: str, other_message: str):
    print(f"message: {message}")
    print(f"other_message: {other_message}")


# TODO: replace the domain and token with your own
ws = WorkflowService(host='https://my-argo-server.com', token='my-auth-token')
w = Workflow('diamond-task-template', ws)

# NOTE: task_template is specified once and invocations of task_template.task(...)
# provide only task name and args.
task_template = TaskTemplate(
    'A',
    say,
    [
        {
            'message': "default value for param 'message'",
            "other_message": {"default": {"value": {"for": "other_message"}}},
        }
    ],
)

a = task_template.task(
    'A-task',
    [
        {
            'message': 'This is task A-0!',
            "other_message": (
                "Providing list of args greater than 1 uses "
                "'withItems' mechanism and needs all params to be specified"
            ),
        },
        {
            'message': 'This is task A-1!',
            "other_message": "This is other_message for A-1!",
        },
    ],
)
b = task_template.task('B-task', [{'message': 'This is task B!'}])
c = task_template.task('C-task', [{'other_message': 'This is task C!'}])
d = task_template.task(
    'D-task',
    [
        {
            'message': {
                "dicted": "message with non-alpanumeric characters: !@#$%^&*()_-+=;|<.>/?"
            }
        }
    ],
)

a.next(b)  # a >> b
a.next(c)  # a >> c
b.next(d)  # b >> d
c.next(d)  # c >> d

w.add_tasks(a, b, c, d)
w.create()
