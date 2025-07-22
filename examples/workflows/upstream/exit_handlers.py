from hera.workflows import Container, Step, Steps, Workflow

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="exit-handlers-",
    entrypoint="intentional-fail",
    on_exit="exit-handler",
) as w:
    Container(
        name="intentional-fail",
        args=["echo intentional failure; exit 1"],
        command=["sh", "-c"],
        image="alpine:latest",
    )
    with Steps(
        name="exit-handler",
    ) as invocator:
        with invocator.parallel():
            Step(
                name="notify",
                template="send-email",
            )
            Step(
                name="celebrate",
                template="celebrate",
                when="{{workflow.status}} == Succeeded",
            )
            Step(
                name="cry",
                template="cry",
                when="{{workflow.status}} != Succeeded",
            )
    Container(
        name="send-email",
        args=[
            "echo send e-mail: {{workflow.name}} {{workflow.status}} {{workflow.duration}}. Failed steps {{workflow.failures}}"
        ],
        command=["sh", "-c"],
        image="alpine:latest",
    )
    Container(
        name="celebrate",
        args=["echo hooray!"],
        command=["sh", "-c"],
        image="alpine:latest",
    )
    Container(
        name="cry",
        args=["echo boohoo!"],
        command=["sh", "-c"],
        image="alpine:latest",
    )
