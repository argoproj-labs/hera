from hera.workflows import (
    Parameter,
    Step,
    Steps,
    Workflow,
    models as m,
)

with Workflow(generate_name="workflow-template-steps-", entrypoint="hello-hello-hello") as w:
    with Steps(name="hello-hello-hello") as s:
        Step(
            name="hello1",
            template_ref=m.TemplateRef(
                name="workflow-template-print-message",
                template="print-message",
            ),
            arguments=Parameter(name="message", value="hello1"),
        )
        with s.parallel():
            Step(
                name="hello2a",
                template_ref=m.TemplateRef(
                    name="cluster-workflow-template-inner-steps",
                    template="inner-steps",
                    cluster_scope=True,
                ),
                arguments=Parameter(name="message", value="hello2a"),
            )
            Step(
                name="hello2b",
                template_ref=m.TemplateRef(
                    name="workflow-template-print-message",
                    template="print-message",
                ),
                arguments=Parameter(name="message", value="hello2b"),
            )
