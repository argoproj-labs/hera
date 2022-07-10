"""This example showcases how to run a workflow with a previously generated WorkflowTemplate with Hera"""
from hera import Workflow, WorkflowService

w = Workflow(
    'workflow-with-template-ref',
    service=WorkflowService(host='my-argo-server.com', token='my-auth-token'),
    workflow_template_ref="coin-flip-template",
)
w.create()
