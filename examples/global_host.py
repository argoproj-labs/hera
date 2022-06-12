"""This example showcases how to set an Argo Workflows host and token at a global level"""

from hera import Task, Workflow, set_global_host, set_global_token

set_global_token('token')
set_global_host('http://localhost:2746')


def p(m):
    print(m)


w = Workflow('w')  # this uses a service with the global token and host
t = Task('t', p, [{'m': 'hello'}])
w.add_task(t)
w.create()
