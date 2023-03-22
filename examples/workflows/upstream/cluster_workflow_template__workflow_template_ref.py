from hera.workflows import Workflow
from hera.workflows.models import WorkflowTemplateRef

wt_ref = WorkflowTemplateRef(name="cluster-workflow-template-submittable", cluster_scope=True)

with Workflow(
    generate_name="cluster-workflow-template-hello-world-",
    workflow_template_ref=wt_ref,
) as w:
    pass
