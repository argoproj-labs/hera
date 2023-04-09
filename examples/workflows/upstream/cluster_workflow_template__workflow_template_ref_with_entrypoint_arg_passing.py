from hera.workflows import (
    Parameter,
    Workflow,
    models as m,
)

w = Workflow(
    generate_name="cluster-workflow-template-hello-world-",
    entrypoint="whalesay-template",
    arguments=Parameter(name="message", value="hello world"),
    workflow_template_ref=m.WorkflowTemplateRef(
        name="cluster-workflow-template-whalesay-template",
        cluster_scope=True,
    ),
)
