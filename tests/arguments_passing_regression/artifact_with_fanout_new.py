from hera.workflows import DAG, Artifact, NoneArchiveStrategy, Workflow, script


@script(outputs=Artifact(name="out-art", path="/tmp/file", archive=NoneArchiveStrategy()))
def writer():
    import json

    with open("/tmp/file", "w+") as f:
        for i in range(10):
            f.write(json.dumps(i) + "\n")


@script(inputs=Artifact(name="in-art", path="/tmp/file"), use_func_params_in_call=True)
def fanout():
    import json
    import sys

    indices = []
    with open("/tmp/file", "r") as f:
        for line in f.readlines():
            indices.append(line.strip())
    json.dump(indices, sys.stdout)


@script(use_func_params_in_call=True)
def consumer(i: int):
    print(i)


with Workflow(generate_name="artifact-with-fanout-", entrypoint="d") as w:
    with DAG(name="d"):
        w_ = writer()
        f = fanout(w_.get_artifact("out-art").as_name("in-art"))
        c = consumer().with_(with_param=f.result)
        w_ >> f >> c
