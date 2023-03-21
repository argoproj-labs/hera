from hera.workflows import Container, Step, Steps, Workflow

container = Container(image="argoproj/argosay:v2")

with Workflow(
    generate_name="steps-inline-",
    entrypoint="main",
    annotations={
        "workflows.argoproj.io/description": ("This workflow demonstrates running a steps with inline templates."),
        "workflows.argoproj.io/version": ">= 3.2.0",
    },
) as w:
    with Steps(name="main"):
        Step(name="a", inline=container)
