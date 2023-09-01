from hera.workflows import DAG, Workflow, script


@script(directly_callable=True)
def foo(p):
    if p < 0.5:
        raise Exception(p)
    print(42)


with Workflow(generate_name="complex-deps-", entrypoint="d") as w:
    with DAG(name="d"):
        A = foo(0.6).with_(name="a")
        B = foo(0.3).with_(name="b")
        C = foo(0.7).with_(name="c")
        D = foo(0.9).with_(name="d")
        # here, D depends on A, B, and C. If A succeeds and one of B or C fails, D still runs
        A >> [B, C], [A, (B | C)] >> D
