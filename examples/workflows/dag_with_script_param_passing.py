from hera.workflows import DAG, Parameter, Task, Workflow, script


@script()
def out():
    print(42)


@script()
def in_(a):
    print(a)


with Workflow(generate_name="script-param-passing-", entrypoint="d") as w:
    with DAG(name="d"):
        t1: Task = out()
        t2 = in_(arguments=Parameter(name="a", value=t1.result))
        t1 >> t2
