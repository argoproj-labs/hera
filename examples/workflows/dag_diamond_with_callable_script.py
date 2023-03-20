from hera.workflows import (
    DAG,
    Parameter,
    Script,
    Workflow,
)


def my_print_script(message):
    print(message)


def get_script(callable):
    # note that we have the _option_ to set `inputs=Parameter(name="message")`, but Hera infers the `Parameter`s
    # that are necessary based on the passed in callable!
    return Script(
        name=callable.__name__.replace("_", "-"),
        source=callable,
        add_cwd_to_sys_path=False,
        image="python:alpine3.6",
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
