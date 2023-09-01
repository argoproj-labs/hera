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
        directly_callable=True,
    )


with Workflow(
    generate_name="dag-diamond-",
    entrypoint="diamond",
) as w:
    echo = get_script(my_print_script)

    with DAG(name="diamond"):
        A = echo("A").with_(name="A")
        B = echo("B").with_(name="B")
        C = echo("C").with_(name="C")
        D = echo("D").with_(name="D")
        A >> [B, C] >> D
