from hera.workflows import DAG, Workflow, script


@script()
def foo(a, b=42, c=None):
    print(a, b, c)


with Workflow(generate_name="script-default-params-", entrypoint="d") as w:
    with DAG(name="d"):
        foo(name="b-unset-c-unset", arguments={"a": 1})
        foo(name="b-set-c-unset", arguments={"a": 1, "b": 2})
        foo(name="b-unset-c-set", arguments={"a": 1, "c": 2})
        foo(name="b-set-c-set", arguments={"a": 1, "b": 2, "c": 3})
