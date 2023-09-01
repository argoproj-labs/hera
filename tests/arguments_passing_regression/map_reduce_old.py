"""
This is a map reduce example from the upstream Argo Workflows repository. This is not part of the upstream examples
folder for workflows because the upstream example is not formatted according to PEP recommendations.

See the upstream example [here](https://github.com/argoproj/argo-workflows/blob/master/examples/map-reduce.yaml).
"""
from hera.workflows import DAG, Artifact, NoneArchiveStrategy, Parameter, S3Artifact, Workflow, script


@script(
    image="python:alpine3.6",
    outputs=S3Artifact(name="parts", path="/mnt/out", archive=NoneArchiveStrategy(), key="{{workflow.name}}/parts"),
)
def split(num_parts: int) -> None:
    import json
    import os
    import sys

    os.mkdir("/mnt/out")

    part_ids = list(map_(lambda x: str(x), range(num_parts)))
    for i, part_id in enumerate(part_ids, start=1):
        with open("/mnt/out/" + part_id + ".json", "w") as f:
            json.dump({"foo": i}, f)
    json.dump(part_ids, sys.stdout)


@script(
    image="python:alpine3.6",
    inputs=Artifact(name="part", path="/mnt/in/part.json"),
    outputs=S3Artifact(
        name="part",
        path="/mnt/out/part.json",
        archive=NoneArchiveStrategy(),
        key="{{workflow.name}}/results/{{inputs.parameters.part_id}}.json",
    ),
)
def map_() -> None:
    import json
    import os

    os.mkdir("/mnt/out")
    with open("/mnt/in/part.json") as f:
        part = json.load(f)
    with open("/mnt/out/part.json", "w") as f:
        json.dump({"bar": part["foo"] * 2}, f)


@script(
    image="python:alpine3.6",
    inputs=S3Artifact(name="results", path="/mnt/in", key="{{workflow.name}}/results"),
    outputs=S3Artifact(
        name="total", path="/mnt/out/total.json", archive=NoneArchiveStrategy(), key="{{workflow.name}}/total.json"
    ),
)
def reduce() -> None:
    import json
    import os

    os.mkdir("/mnt/out")

    total = 0
    for f in list(map_(lambda x: open("/mnt/in/" + x), os.listdir("/mnt/in"))):
        result = json.load(f)
        total = total + result["bar"]
    with open("/mnt/out/total.json", "w") as f:
        json.dump({"total": total}, f)


with Workflow(generate_name="map-reduce-", entrypoint="main", arguments=Parameter(name="num_parts", value="4")) as w:
    with DAG(name="main"):
        s = split(arguments=Parameter(name="num_parts", value="{{workflow.parameters.numParts}}"))
        m = map_(
            with_param=s.result,
            arguments=S3Artifact(name="part", key="{{workflow.name}}/parts/{{item}}.json"),
        )
        s >> m >> reduce()
