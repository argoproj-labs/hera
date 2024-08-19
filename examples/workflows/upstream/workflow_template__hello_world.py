from hera.workflows import Step, Steps, Workflow
from hera.workflows.models import TemplateRef

with Workflow(
    generate_name="workflow-template-hello-world-",
    entrypoint="hello-world-from-templateRef",
) as w:
    print_message_template_ref = TemplateRef(
        name="workflow-template-print-message",
        template="print-message",
    )
    with Steps(name="hello-world-from-templateRef"):
        Step(
            name="call-print-message",
            template_ref=print_message_template_ref,
            arguments={"message": "hello world"},
        )
