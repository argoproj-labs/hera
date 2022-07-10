from hera import Task, Workflow, WorkflowService, GlobalInputParameter, Variable

from dyno.clients.middleware.client_factory import generate_dynet_iap_oauth_token
from hera import set_global_token, set_global_host

set_global_token(generate_dynet_iap_oauth_token().token)
set_global_host('https://argo.dynet.ai')


def foo(v):
    print(v)


with Workflow('global-parameters', variables=[Variable('v', '42')]) as w:
    Task('t', foo, inputs=[GlobalInputParameter('v', 'v')])

w.create()
