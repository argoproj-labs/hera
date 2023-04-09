from hera.workflows import Container, Parameter, Steps, WorkflowTemplate

with WorkflowTemplate(
    name="event-consumer",
    entrypoint="main",
    arguments=Parameter(name="salutation", value="hello"),
) as w:
    say = Container(
        name="argosay",
        image="argoproj/argosay:v2",
        inputs=[
            Parameter(name="salutation"),
            Parameter(name="appellation"),
        ],
        args=["echo", "{{inputs.parameters.salutation}} {{inputs.parameters.appellation}}"],
    )
    with Steps(name="main"):
        say(
            name="a",
            arguments=[
                Parameter(name="salutation", value="{{workflow.parameters.salutation}}"),
                Parameter(name="appellation", value="{{workflow.parameters.appellation}}"),
            ],
        )
