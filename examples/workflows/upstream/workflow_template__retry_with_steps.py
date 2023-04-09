from hera.workflows import (
    Step,
    Steps,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="workflow-template-retry-with-steps-",
    entrypoint="retry-with-steps",
) as w:
    with Steps(name="retry-with-steps") as s:
        Step(
            name="hello1",
            template_ref=m.TemplateRef(
                name="workflow-template-random-fail-template",
                template="random-fail-template",
            ),
        )
        with s.parallel():
            Step(
                name="hello2a",
                template_ref=m.TemplateRef(
                    name="workflow-template-random-fail-template",
                    template="random-fail-template",
                ),
            )
            Step(
                name="hello2b",
                template_ref=m.TemplateRef(
                    name="workflow-template-random-fail-template",
                    template="random-fail-template",
                ),
            )
