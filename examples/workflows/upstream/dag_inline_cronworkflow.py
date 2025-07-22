from hera.workflows import CronWorkflow
from hera.workflows.models import WorkflowTemplateRef

with CronWorkflow(
    api_version="argoproj.io/v1alpha1",
    kind="CronWorkflow",
    annotations={
        "workflows.argoproj.io/description": "This example demonstrates running cron workflow that has a DAG with inline templates.\n",
        "workflows.argoproj.io/version": ">= 3.2.0",
    },
    name="dag-inline",
    workflow_template_ref=WorkflowTemplateRef(
        name="dag-inline",
    ),
    schedule="*/5 * * * *",
) as w:
    pass
