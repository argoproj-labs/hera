"""This example showcases how to run a workflow with a previously generated WorkflowTemplate with Hera"""
from hera import Workflow

Workflow("workflow-with-template-ref", workflow_template_ref="coin-flip-template").create()
