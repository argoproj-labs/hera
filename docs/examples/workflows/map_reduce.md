# Map Reduce



This is a map reduce example from the upstream Argo Workflows repository. This is not part of the upstream examples
folder for workflows because the upstream example is not formatted properly


=== "Hera"

    ```python linenums="1"
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

        part_ids = list(map(lambda x: str(x), range(num_parts)))
        for i, part_id in enumerate(part_ids, start=1):  # fmt: skip
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
            key="{{workflow.name}}/results/{{inputs.parameters.partId}}.json",
        ),
    )
    def map(part_id: str) -> None:
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
        for f in list(map(lambda x: open("/mnt/in/" + x), os.listdir("/mnt/in"))):
            result = json.load(f)
            total = total + result["bar"]
        with open("/mnt/out/total.json", "w") as f:
            json.dump({"total": total}, f)


    with Workflow(generate_name="map-reduce-", entrypoint="main", arguments=Parameter(name="num_parts", value="4")) as w:
        with DAG(name="main"):
            s = split(arguments=Parameter(name="num_parts", value="{{workflow.parameters.numParts}}"))
            m = map(
                with_param=s.result,
                arguments=S3Artifact(name="part", key="{{workflow.name}}/parts/{{item}}.json"),
            )
            s >> m >> reduce()
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: map-reduce-
    spec:
      arguments:
        parameters:
        - name: num_parts
          value: '4'
      entrypoint: main
      templates:
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: num_parts
                value: '{{workflow.parameters.numParts}}'
            name: split
            template: split
          - arguments:
              artifacts:
              - name: part
                s3:
                  key: '{{workflow.name}}/parts/{{item}}.json'
              parameters:
              - name: part_id
                value: '{{item}}'
            depends: split
            name: map
            template: map
            withParam: '{{tasks.split.outputs.result}}'
          - depends: map
            name: reduce
            template: reduce
        name: main
      - inputs:
          parameters:
          - name: num_parts
        name: split
        outputs:
          artifacts:
          - archive:
              none: {}
            name: parts
            path: /mnt/out
            s3:
              key: '{{workflow.name}}/parts'
        script:
          command:
          - python
          image: python:alpine3.6
          source: "import os\nimport sys\nsys.path.append(os.getcwd())\nimport json\n\
            try: num_parts = json.loads(r'''{{inputs.parameters.num_parts}}''')\nexcept:\
            \ num_parts = r'''{{inputs.parameters.num_parts}}'''\n\nimport json\nimport\
            \ os\nimport sys\nos.mkdir('/mnt/out')\npart_ids = list(map(lambda x: str(x),\
            \ range(num_parts)))\nfor i, part_id in enumerate(part_ids, start=1):\n  \
            \  with open('/mnt/out/' + part_id + '.json', 'w') as f:\n        json.dump({'foo':\
            \ i}, f)\njson.dump(part_ids, sys.stdout)"
      - inputs:
          artifacts:
          - name: part
            path: /mnt/in/part.json
          parameters:
          - name: part_id
        name: map
        outputs:
          artifacts:
          - archive:
              none: {}
            name: part
            path: /mnt/out/part.json
            s3:
              key: '{{workflow.name}}/results/{{inputs.parameters.partId}}.json'
        script:
          command:
          - python
          image: python:alpine3.6
          source: "import os\nimport sys\nsys.path.append(os.getcwd())\nimport json\n\
            try: part_id = json.loads(r'''{{inputs.parameters.part_id}}''')\nexcept: part_id\
            \ = r'''{{inputs.parameters.part_id}}'''\n\nimport json\nimport os\nos.mkdir('/mnt/out')\n\
            with open('/mnt/in/part.json') as f:\n    part = json.load(f)\nwith open('/mnt/out/part.json',\
            \ 'w') as f:\n    json.dump({'bar': part['foo'] * 2}, f)"
      - inputs:
          artifacts:
          - name: results
            path: /mnt/in
            s3:
              key: '{{workflow.name}}/results'
        name: reduce
        outputs:
          artifacts:
          - archive:
              none: {}
            name: total
            path: /mnt/out/total.json
            s3:
              key: '{{workflow.name}}/total.json'
        script:
          command:
          - python
          image: python:alpine3.6
          source: "import os\nimport sys\nsys.path.append(os.getcwd())\nimport json\n\
            import os\nos.mkdir('/mnt/out')\ntotal = 0\nfor f in list(map(lambda x: open('/mnt/in/'\
            \ + x), os.listdir('/mnt/in'))):\n    result = json.load(f)\n    total = total\
            \ + result['bar']\nwith open('/mnt/out/total.json', 'w') as f:\n    json.dump({'total':\
            \ total}, f)"
    ```

