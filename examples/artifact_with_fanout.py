from hera import Artifact, Task, Workflow


def writer():
    import json

    with open("/file", "w+") as f:
        for i in range(10):
            f.write(f"{json.dumps(i)}\n")


def fanout():
    import json
    import sys

    indices = []
    with open("/file", "r") as f:
        for line in f.readlines():
            indices.append(line.strip())
    json.dump(indices, sys.stdout)


def consumer(i: int):
    print(i)


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow(generate_name="artifact-with-fanout-") as w:
    w_t = Task("writer", writer, outputs=[Artifact(name="test", path="/file")])
    f_t = Task(
        "fanout",
        fanout,
        inputs=[w_t.get_artifact("test")],
    )
    c_t = Task("consumer", consumer, with_param=f_t.get_result())
    w_t >> f_t >> c_t

w.create()
