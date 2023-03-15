from hera.workflows import (
    DAG,
    Parameter,
    Script,
    Workflow,
)


def my_print_script(message):
    print(message)


def get_script(callable):
    return Script(
        name=callable.__name__.replace("_", "-"),
        source=callable,
        add_cwd_to_sys_path=False,
        image="python:alpine3.6",
        inputs=[Parameter(name="message")],
    )


with Workflow(
    generate_name="dag-diamond-",
    entrypoint="diamond",
) as w:
    echo = get_script(my_print_script)

    with DAG(name="diamond"):
        A = echo(name="A", arguments=[Parameter(name="message", value="A")])
        B = echo(name="B", arguments=[Parameter(name="message", value="B")])
        C = echo(name="C", arguments=[Parameter(name="message", value="C")])
        D = echo(name="D", arguments=[Parameter(name="message", value="D")])
        A >> [B, C] >> D
