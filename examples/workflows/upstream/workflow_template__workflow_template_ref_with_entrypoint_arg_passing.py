from hera.workflows import (
    Parameter,
    Workflow,
    models as m,
)

w = Workflow(
    generate_name="workflow-template-hello-world-",
    entrypoint="print-message",
    workflow_template_ref=m.WorkflowTemplateRef(
        name="workflow-template-print-message",
    ),
    arguments=Parameter(name="message", value="hello world"),
)
