"""This example showcases how to run a workflow with a previously generated WorkflowTemplate with Hera"""
from hera.workflow import Workflow
from hera.workflow_service import WorkflowService

# TODO: replace the domain and token with your own
ws = WorkflowService(host='', verify_ssl=False, token='')
w = Workflow('wf-template-testing', ws, namespace="argo", workflow_template_ref="coin-flip-template")

w.create()
