from hera.expr import g
from hera.workflows import (
    DAG,
    ContainerNode,
    ContainerSet,
    Parameter,
    Script,
    Task,
    Workflow,
    models as m,
)


def _check():
    assert "{{inputs.parameters.x}}" == "hi"


with Workflow(
    generate_name="outputs-result-",
    entrypoint="main",
) as w:
    with ContainerSet(name="group") as group:
        ContainerNode(name="main", image="python:alpine3.6", command=["python", "-c"], args=['print("hi")\n'])

    verify = Script(
        source=_check,
        image="python:alpine3.6",
        command=["python"],
        inputs=[Parameter(name="x")],
        add_cwd_to_sys_path=False,
        name="verify",
    )
    with DAG(name="main") as dag:
        a = Task(name="a", template=group)
        b = Task(
            name="b",
            arguments=m.Arguments(parameters=[Parameter(name="x", value=f"{g.tasks.a.outputs.result:$}")]),
            template=verify,
            dependencies=["a"],
        )
