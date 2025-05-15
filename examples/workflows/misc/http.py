from hera.workflows import Parameter, Steps, Workflow, script
from hera.workflows.models import ValueFrom


@script(
    outputs=[
        Parameter(name="hello-output", value_from=ValueFrom(path="/tmp/hello_world.txt")),
    ]
)
def hello_to_file():
    with open("/tmp/hello_world.txt", "w") as f:
        f.write("Hello World!")


@script()
def repeat_back(message: str):
    print(f"You just said: '{message}'")


with Workflow(
    generate_name="hello-world-parameter-passing-",
    entrypoint="steps",
) as w:
    with Steps(name="steps"):
        hello_world_step = hello_to_file()
        repeat_back(arguments={"message": hello_world_step.get_parameter("hello-output")})