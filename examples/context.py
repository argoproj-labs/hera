from hera import Workflow, Task, WorkflowService

with Workflow('context', service=WorkflowService(host='https://my-argo-server.com', token='my-auth-token')) as w:
    Task('cowsay', image='docker/whalesay', command=['cowsay', 'foo'])

w.create()
