from hera.workflows import DAG, Artifact, Workflow, script


@script(outputs=Artifact(name="test", path="/file"))
def writer():
    import json

    with open("/file", "w+") as f:
        for i in range(10):
            f.write(f"{json.dumps(i)}\n")


@script(inputs=Artifact(name="test", path="/file"))
def fanout():
    import json
    import sys

    indices = []
    with open("/file", "r") as f:
        for line in f.readlines():
            indices.append(line.strip())
    json.dump(indices, sys.stdout)


@script()
def consumer(i: int):
    print(i)


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow(generate_name="artifact-with-fanout-", entrypoint="d") as w:
    with DAG(name="d"):
        w_ = writer()
        f = fanout(arguments=w_.get_artifact("test"))
        c = consumer(with_param=f.result)
        w_ >> f >> c
