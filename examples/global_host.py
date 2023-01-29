"""This example showcases how to set an Argo Workflows host and token at a global level"""

from hera import GlobalConfig, Task, Workflow

GlobalConfig.token = "token"
GlobalConfig.token = "http://example.argo"


def p(m):
    print(m)


with Workflow(generate_name="global-host-") as w:  # this uses a service with the global token and host
    Task("t", p, [{"m": "hello"}])

w.create()
