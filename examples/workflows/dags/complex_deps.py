"""This example shows how to create more complex dependencies between tasks."""

from hera.workflows import DAG, Workflow, script


@script()
def foo(p):
    if p < 0.5:
        raise Exception(p)
    print(42)


with Workflow(generate_name="complex-deps-", entrypoint="d") as w:
    with DAG(name="d"):
        A = foo(name="a", arguments={"p": 0.6})
        B = foo(name="b", arguments={"p": 0.3})
        C = foo(name="c", arguments={"p": 0.7})
        D = foo(name="d", arguments={"p": 0.9})

        A >> [B, C]
        # here, D depends on A, B, and C. If A succeeds and one of B or C fails, D still runs
        [A, (B | C)] >> D
