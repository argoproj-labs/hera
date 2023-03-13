# Artifact Disable Archive

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/artifact-disable-archive.yaml).



## Hera

```python
from hera.workflows import (
    Artifact,
    Container,
    Step,
    Steps,
    Workflow,
    models as m,
)

with Workflow(generate_name="artifact-disable-archive-", entrypoint="artifact-disable-archive") as w:
    whalesay = Container(
        name="whalesay",
        image="docker/whalesay:latest",
        command=["sh", "-c"],
        args=["cowsay hello world | tee /tmp/hello_world.txt | tee /tmp/hello_world_nc.txt ; sleep 1"],
        outputs=[
            Artifact(name="etc", path="/etc", archive=m.ArchiveStrategy(none=m.NoneStrategy())),
            Artifact(name="hello-txt", path="/tmp/hello_world.txt", archive=m.ArchiveStrategy(none=m.NoneStrategy())),
            Artifact(
                name="hello-txt-nc",
                path="/tmp/hello_world_nc.txt",
                archive=m.ArchiveStrategy(tar=m.TarStrategy(compression_level=0)),
            ),
        ],
    )
    print_message = Container(
        name="print-message",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["cat /tmp/hello.txt && cat /tmp/hello_nc.txt && cd /tmp/etc && find ."],
        inputs=[
            Artifact(name="etc", path="/tmp/etc"),
            Artifact(name="hello-txt", path="/tmp/hello.txt"),
            Artifact(name="hello-txt-nc", path="/tmp/hello_nc.txt"),
        ],
    )
    with Steps(name="artifact-disable-archive") as s:
        Step(name="generate-artifact", template=whalesay)
        Step(
            name="consume-artifact",
            template=print_message,
            arguments=[
                Artifact(name="etc", from_="{{steps.generate-artifact.outputs.artifacts.etc}}"),
                Artifact(name="hello-txt", from_="{{steps.generate-artifact.outputs.artifacts.hello-txt}}"),
                Artifact(name="hello-txt-nc", from_="{{steps.generate-artifact.outputs.artifacts.hello-txt-nc}}"),
            ],
        )
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: artifact-disable-archive-
spec:
  entrypoint: artifact-disable-archive
  templates:
  - container:
      args:
      - cowsay hello world | tee /tmp/hello_world.txt | tee /tmp/hello_world_nc.txt
        ; sleep 1
      command:
      - sh
      - -c
      image: docker/whalesay:latest
    name: whalesay
    outputs:
      artifacts:
      - archive:
          none: {}
        name: etc
        path: /etc
      - archive:
          none: {}
        name: hello-txt
        path: /tmp/hello_world.txt
      - archive:
          tar:
            compressionLevel: 0
        name: hello-txt-nc
        path: /tmp/hello_world_nc.txt
  - container:
      args:
      - cat /tmp/hello.txt && cat /tmp/hello_nc.txt && cd /tmp/etc && find .
      command:
      - sh
      - -c
      image: alpine:latest
    inputs:
      artifacts:
      - name: etc
        path: /tmp/etc
      - name: hello-txt
        path: /tmp/hello.txt
      - name: hello-txt-nc
        path: /tmp/hello_nc.txt
    name: print-message
  - name: artifact-disable-archive
    steps:
    - - name: generate-artifact
        template: whalesay
    - - arguments:
          artifacts:
          - from: '{{steps.generate-artifact.outputs.artifacts.etc}}'
            name: etc
          - from: '{{steps.generate-artifact.outputs.artifacts.hello-txt}}'
            name: hello-txt
          - from: '{{steps.generate-artifact.outputs.artifacts.hello-txt-nc}}'
            name: hello-txt-nc
        name: consume-artifact
        template: print-message
```
