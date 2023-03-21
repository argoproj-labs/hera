from hera.workflows import Step, Steps, Workflow
from hera.workflows.models import TemplateRef

with Workflow(
    generate_name="workflow-template-hello-world-",
    entrypoint="whalesay",
) as w:
    whalesay_template_ref = TemplateRef(
        name="workflow-template-whalesay-template",
        template="whalesay-template",
    )
    with Steps(name="whalesay"):
        Step(
            name="call-whalesay-template",
            template_ref=whalesay_template_ref,
            arguments={"message": "hello world"},
        )
