from hera.workflows import DAG, Workflow, script


@script(directly_callable=True)
def foo(a, b=42, c=None):
    print(a, b, c)


with Workflow(generate_name="script-default-params-", entrypoint="d") as w:
    with DAG(name="d"):
        foo(1).with_(name="b-unset-c-unset")
        foo(1, 2).with_(name="b-set-c-unset")
        foo(1, c=2).with_(name="b-unset-c-set")
        foo(1, 2, 3).with_(name="b-set-c-set")
