from hera.workflows import (
    Parameter,
    Workflow,
    models as m,
)

w = Workflow(
    generate_name="workflow-template-hello-world-",
    entrypoint="whalesay-template",
    workflow_template_ref=m.WorkflowTemplateRef(
        name="workflow-template-whalesay-template",
    ),
    arguments=Parameter(name="message", value="hello world"),
)
