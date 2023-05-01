#
from hera.workflows import DAG, Artifact, NoneArchiveStrategy, Parameter, S3Artifact, Workflow, script

# fmt: off
@script(
    image="python:alpine3.6",
    outputs=S3Artifact(name="parts", path="/mnt/out", archive=NoneArchiveStrategy(), key="{{workflow.name}}/parts"),
)
def split(numParts: int) -> None:
    import json
    import os
    import sys
    os.mkdir("/mnt/out")
    partIds = list(map(lambda x: str(x), range({{inputs.parameters.numParts}})))
    for i, partId in enumerate(partIds, start=1):
        with open("/mnt/out/" + partId + ".json", "w") as f:
            json.dump({"foo": i}, f)
    json.dump(partIds, sys.stdout)
# fmt: on

@script(
    image="python:alpine3.6",
    inputs=Artifact(name="part", path="/mnt/in/part.json"),
    outputs=S3Artifact(
        name="part",
        path="/mnt/out/part.json",
        archive=NoneArchiveStrategy(),
        key="{{workflow.name}}/results/{{inputs.parameters.partId}}.json",
    ),
)
def map(partId: str) -> None:
    import json
    import os
    import sys
    os.mkdir("/mnt/out")
    with open("/mnt/in/part.json") as f:
        part = json.load(f)
    with open("/mnt/out/part.json", "w") as f:
        json.dump({"bar": part["foo"] * 2}, f)
# fmt: on

# fmt: off
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
    import sys
    total = 0
    os.mkdir("/mnt/out")
    for f in list(map(lambda x: open("/mnt/in/" + x), os.listdir("/mnt/in"))):
        result = json.load(f)
        total = total + result["bar"]
    with open("/mnt/out/total.json", "w") as f:
        json.dump({"total": total}, f)
# fmt: on

with Workflow(generate_name="map-reduce-", entrypoint="main", arguments=Parameter(name="numParts", value="4")) as w:
    with DAG(name="main"):
        s = split(arguments=Parameter(name="numParts", value="{{workflow.parameters.numParts}}"))
        m = map(
            with_param=s.result,
            arguments=S3Artifact(name="part", key="{{workflow.name}}/parts/{{item}}.json"),
        )
        r = reduce()
        s >> m >> r

print(w.to_yaml())