from hera.workflows import Workflow
from hera.workflows.models import WorkflowTemplateRef

wt_ref = WorkflowTemplateRef(name="workflow-template-submittable")

w = Workflow(
    generate_name="workflow-template-hello-world-",
    workflow_template_ref=wt_ref,
)
