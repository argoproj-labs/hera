from hera.workflows import (
    DAG,
    Parameter,
    Task,
    Workflow,
    models as m,
    script,
)


@script(outputs=[Parameter(name="a", value_from=m.ValueFrom(path="/test"))])
def out():
    with open("/test", "w") as f_out:
        f_out.write("test")


@script(use_func_params_in_call=True)
def in_(a):
    print(a)


with Workflow(generate_name="script-output-param-passing-", entrypoint="d") as w:
    with DAG(name="d"):
        t1: Task = out()
        t2 = in_(t1.get_parameter("a"))
        t1 >> t2
