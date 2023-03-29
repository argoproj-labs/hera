from hera.workflows import DAG, Workflow, script


@script()
def foo(a, b=42):
    print(a, b)


with Workflow(generate_name="script-default-params-", entrypoint="d") as w:
    with DAG(name="d"):
        foo(name="b-set", arguments={"a": 1, "b": 2})
        foo(name="b-unset", arguments={"a": 1})
