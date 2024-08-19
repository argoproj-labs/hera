from hera.workflows import (
    DAG,
    Parameter,
    Task,
    Workflow,
    models as m,
)

with Workflow(generate_name="workflow-template-dag-diamond-", entrypoint="diamond") as w:
    with DAG(name="diamond") as dag:
        A = Task(
            name="A",
            template_ref=m.TemplateRef(
                name="cluster-workflow-template-print-message", template="print-message", cluster_scope=True
            ),
            arguments=Parameter(name="message", value="A"),
        )
        B = Task(
            name="B",
            template_ref=m.TemplateRef(
                name="cluster-workflow-template-print-message", template="print-message", cluster_scope=True
            ),
            arguments=Parameter(name="message", value="B"),
        )
        C = Task(
            name="C",
            template_ref=m.TemplateRef(
                name="cluster-workflow-template-inner-dag", template="inner-diamond", cluster_scope=True
            ),
        )
        D = Task(
            name="D",
            template_ref=m.TemplateRef(
                name="cluster-workflow-template-print-message", template="print-message", cluster_scope=True
            ),
            arguments=Parameter(name="message", value="D"),
        )
        A >> [B, C] >> D
