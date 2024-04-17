from hera.workflows import DAG, Workflow, script


@script(env={"a": 1, "b": 2, "c": 3})
def env():
    import os

    # note that env params come in as strings
    assert os.environ["a"] == "1", os.environ["a"]
    assert os.environ["b"] == "2", os.environ["b"]
    assert os.environ["c"] == "3", os.environ["c"]


with Workflow(generate_name="multi-env-", entrypoint="d") as w:
    with DAG(name="d"):
        env()
