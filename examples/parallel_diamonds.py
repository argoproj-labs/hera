"""This example showcases how one can schedule a diamond structure with parallel processing through Hera"""
from hera import Task, Workflow, WorkflowService


def say(message: str):
    print(message)


# TODO: replace the domain and token with your own
ws = WorkflowService(host='my-argo-server.com', token='my-auth-token')
w = Workflow('parallel-diamonds', ws)
a = Task(
    'A', say, [{'message': 'This is task A.1!'}, {'message': 'This is task A.2!'}, {'message': 'This is task A.3!'}]
)
b = Task(
    'B', say, [{'message': 'This is task B.1!'}, {'message': 'This is task B.2!'}, {'message': 'This is task B.3!'}]
)
c = Task(
    'C', say, [{'message': 'This is task C.1!'}, {'message': 'This is task C.2!'}, {'message': 'This is task C.3!'}]
)
d = Task(
    'D', say, [{'message': 'This is task D.1!'}, {'message': 'This is task D.2!'}, {'message': 'This is task D.3!'}]
)

a >> b  # a.next(b)
a >> c  # a.next(c)
b >> d  # b.next(d)
c >> d  # c.next(d)

w.add_tasks(a, b, c, d)
w.create()
