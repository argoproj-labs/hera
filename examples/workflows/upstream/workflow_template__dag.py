from hera.workflows import DAG, Task, Workflow
from hera.workflows.models import TemplateRef

with Workflow(
    generate_name="workflow-template-dag-diamond-",
    entrypoint="diamond",
) as w:
    whalesay_template_ref = TemplateRef(name="workflow-template-whalesay-template", template="whalesay-template")
    inner_template_ref = TemplateRef(name="workflow-template-inner-dag", template="inner-diamond")
    with DAG(name="diamond"):
        A = Task(name="A", template_ref=whalesay_template_ref, arguments={"message": "A"})
        B = Task(name="B", template_ref=whalesay_template_ref, arguments={"message": "B"})
        C = Task(name="C", template_ref=inner_template_ref)
        D = Task(name="D", template_ref=whalesay_template_ref, arguments={"message": "D"})

        A >> [B, C] >> D
