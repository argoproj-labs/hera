# Map Reduce

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/map-reduce.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Script, Task, Workflow
    from hera.workflows.models import (
        ArchiveStrategy,
        Arguments,
        Artifact,
        Inputs,
        NoneStrategy,
        Outputs,
        Parameter,
        S3Artifact,
    )

    with Workflow(
        arguments=Arguments(
            parameters=[
                Parameter(
                    name="numParts",
                    value="4",
                )
            ],
        ),
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        annotations={
            "workflows.argoproj.io/description": 'This workflow demonstrates map-reduce using "key-only" artifacts.\nThe first task "split" produces a number of parts, each in the form of a JSON document, saving it to a bucket.\nEach "map" task then reads those documents, performs a map operation, and writes them out to a new bucket.\nFinally, "reduce" merges all the mapped documents into a final document.\n',
            "workflows.argoproj.io/version": ">= 3.0.0",
        },
        generate_name="map-reduce-",
        entrypoint="main",
    ) as w:
        with DAG(
            name="main",
        ) as invocator:
            Task(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="numParts",
                            value="{{workflow.parameters.numParts}}",
                        )
                    ],
                ),
                name="split",
                template="split",
            )
            Task(
                with_param="{{tasks.split.outputs.result}}",
                arguments=Arguments(
                    artifacts=[
                        Artifact(
                            name="part",
                            s3=S3Artifact(
                                key="{{workflow.name}}/parts/{{item}}.json",
                            ),
                        )
                    ],
                    parameters=[
                        Parameter(
                            name="partId",
                            value="{{item}}",
                        )
                    ],
                ),
                name="map",
                template="map",
                depends="split",
            )
            Task(
                name="reduce",
                template="reduce",
                depends="map",
            )
        Script(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="numParts",
                    )
                ],
            ),
            name="split",
            outputs=Outputs(
                artifacts=[
                    Artifact(
                        archive=ArchiveStrategy(
                            none=NoneStrategy(),
                        ),
                        name="parts",
                        path="/mnt/out",
                        s3=S3Artifact(
                            key="{{workflow.name}}/parts/",
                        ),
                    )
                ],
            ),
            command=["python"],
            image="python:alpine3.6",
            source='import json\nimport os\nimport sys\nos.mkdir("/mnt/out")\npartIds = list(map(lambda x: str(x), range({{inputs.parameters.numParts}})))\nfor i, partId in enumerate(partIds, start=1):\n  with open("/mnt/out/" + partId + ".json", "w") as f:\n    json.dump({"foo": i}, f)\njson.dump(partIds, sys.stdout)\n',
        )
        Script(
            inputs=Inputs(
                artifacts=[
                    Artifact(
                        name="part",
                        path="/mnt/in/part.json",
                    )
                ],
                parameters=[
                    Parameter(
                        name="partId",
                    )
                ],
            ),
            name="map",
            outputs=Outputs(
                artifacts=[
                    Artifact(
                        archive=ArchiveStrategy(
                            none=NoneStrategy(),
                        ),
                        name="part",
                        path="/mnt/out/part.json",
                        s3=S3Artifact(
                            key="{{workflow.name}}/results/{{inputs.parameters.partId}}.json",
                        ),
                    )
                ],
            ),
            command=["python"],
            image="python:alpine3.6",
            source='import json\nimport os\nimport sys\nos.mkdir("/mnt/out")\nwith open("/mnt/in/part.json") as f:\n  part = json.load(f)\nwith open("/mnt/out/part.json", "w") as f:\n  json.dump({"bar": part["foo"] * 2}, f)\n',
        )
        Script(
            inputs=Inputs(
                artifacts=[
                    Artifact(
                        name="results",
                        path="/mnt/in",
                        s3=S3Artifact(
                            key="{{workflow.name}}/results",
                        ),
                    )
                ],
            ),
            name="reduce",
            outputs=Outputs(
                artifacts=[
                    Artifact(
                        archive=ArchiveStrategy(
                            none=NoneStrategy(),
                        ),
                        name="total",
                        path="/mnt/out/total.json",
                        s3=S3Artifact(
                            key="{{workflow.name}}/total.json",
                        ),
                    )
                ],
            ),
            command=["python"],
            image="python:alpine3.6",
            source='import json\nimport os\nimport sys\ntotal = 0\nos.mkdir("/mnt/out")\nfor f in list(map(lambda x: open("/mnt/in/" + x), os.listdir("/mnt/in"))):\n  result = json.load(f)\n  total = total + result["bar"]\nwith open("/mnt/out/total.json" , "w") as f:\n  json.dump({"total": total}, f)\n',
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: map-reduce-
      annotations:
        workflows.argoproj.io/description: |
          This workflow demonstrates map-reduce using "key-only" artifacts.
          The first task "split" produces a number of parts, each in the form of a JSON document, saving it to a bucket.
          Each "map" task then reads those documents, performs a map operation, and writes them out to a new bucket.
          Finally, "reduce" merges all the mapped documents into a final document.
        workflows.argoproj.io/version: '>= 3.0.0'
    spec:
      entrypoint: main
      templates:
      - name: main
        dag:
          tasks:
          - name: split
            template: split
            arguments:
              parameters:
              - name: numParts
                value: '{{workflow.parameters.numParts}}'
          - name: map
            depends: split
            template: map
            withParam: '{{tasks.split.outputs.result}}'
            arguments:
              artifacts:
              - name: part
                s3:
                  key: '{{workflow.name}}/parts/{{item}}.json'
              parameters:
              - name: partId
                value: '{{item}}'
          - name: reduce
            depends: map
            template: reduce
      - name: split
        inputs:
          parameters:
          - name: numParts
        outputs:
          artifacts:
          - name: parts
            path: /mnt/out
            archive:
              none: {}
            s3:
              key: '{{workflow.name}}/parts/'
        script:
          image: python:alpine3.6
          source: |
            import json
            import os
            import sys
            os.mkdir("/mnt/out")
            partIds = list(map(lambda x: str(x), range({{inputs.parameters.numParts}})))
            for i, partId in enumerate(partIds, start=1):
              with open("/mnt/out/" + partId + ".json", "w") as f:
                json.dump({"foo": i}, f)
            json.dump(partIds, sys.stdout)
          command:
          - python
      - name: map
        inputs:
          artifacts:
          - name: part
            path: /mnt/in/part.json
          parameters:
          - name: partId
        outputs:
          artifacts:
          - name: part
            path: /mnt/out/part.json
            archive:
              none: {}
            s3:
              key: '{{workflow.name}}/results/{{inputs.parameters.partId}}.json'
        script:
          image: python:alpine3.6
          source: |
            import json
            import os
            import sys
            os.mkdir("/mnt/out")
            with open("/mnt/in/part.json") as f:
              part = json.load(f)
            with open("/mnt/out/part.json", "w") as f:
              json.dump({"bar": part["foo"] * 2}, f)
          command:
          - python
      - name: reduce
        inputs:
          artifacts:
          - name: results
            path: /mnt/in
            s3:
              key: '{{workflow.name}}/results'
        outputs:
          artifacts:
          - name: total
            path: /mnt/out/total.json
            archive:
              none: {}
            s3:
              key: '{{workflow.name}}/total.json'
        script:
          image: python:alpine3.6
          source: |
            import json
            import os
            import sys
            total = 0
            os.mkdir("/mnt/out")
            for f in list(map(lambda x: open("/mnt/in/" + x), os.listdir("/mnt/in"))):
              result = json.load(f)
              total = total + result["bar"]
            with open("/mnt/out/total.json" , "w") as f:
              json.dump({"total": total}, f)
          command:
          - python
      arguments:
        parameters:
        - name: numParts
          value: '4'
    ```

