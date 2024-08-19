from hera.workflows import (
    Parameter,
    Workflow,
    models as m,
)

w = Workflow(
    generate_name="cluster-workflow-template-hello-world-",
    entrypoint="print-message",
    arguments=Parameter(name="message", value="hello world"),
    workflow_template_ref=m.WorkflowTemplateRef(
        name="cluster-workflow-template-print-message",
        cluster_scope=True,
    ),
)
