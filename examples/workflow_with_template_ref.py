"""This example showcases how to run a workflow with a previously generated WorkflowTemplate with Hera"""
from hera import Workflow, WorkflowService

# TODO: replace the domain and token with your own
ws = WorkflowService(host='', verify_ssl=False, token='')
w = Workflow('workflow-with-template-ref', ws, namespace="argo", workflow_template_ref="coin-flip-template")

w.create()
