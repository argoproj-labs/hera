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
        use_func_params_in_call=True,
    )
    with Steps(name="main"):
        say(
            Parameter(name="salutation", value="{{workflow.parameters.salutation}}"),
            Parameter(name="appellation", value="{{workflow.parameters.appellation}}"),
        ).with_(name="a")
