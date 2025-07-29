from hera.workflows import (
    DAG,
    Parameter,
    Task,
    Workflow,
    models as m,
    script,
)


@script(
    outputs=[
        Parameter(name="a", value_from=m.ValueFrom(path="/a")),
        Parameter(name="b", value_from=m.ValueFrom(path="/b")),
        Parameter(name="c", value_from=m.ValueFrom(path="/c")),
    ]
)
def create_some_outputs():
    outputs = ["a", "b", "c"]
    for output in outputs:
        with open(f"/{output}", "w") as f_out:
            f_out.write(f"This is {output}")


@script(
    outputs=[
        Parameter(name="d", value_from=m.ValueFrom(path="/d")),
        Parameter(name="e", value_from=m.ValueFrom(path="/e")),
    ]
)
def create_more_outputs():
    outputs = ["d", "e"]
    for output in outputs:
        with open(f"/{output}", "w") as f_out:
            f_out.write(f"This is {output}")


@script()
def use_some_inputs(a, b, c):
    print(a, b, c)


@script()
def use_more_inputs(a, b, c, d, e):
    print(a, b, c, d, e)


with Workflow(generate_name="map-outputs-to-inputs-", entrypoint="dag") as w:
    with DAG(name="dag"):
        t1: Task = create_some_outputs()
        t2 = use_some_inputs(arguments=t1.get_outputs())

        t3: Task = create_more_outputs()
        t4 = use_more_inputs(arguments=t1.get_outputs() + t3.get_outputs())

        t1 >> t2
        [t1, t3] >> t4
