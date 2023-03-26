# Hdfs Artifact

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/hdfs-artifact.yaml).



## Hera

```python
from hera.workflows import (
    Artifact,
    Container,
    HDFSArtifact,
    Step,
    Steps,
    Workflow,
)

with Workflow(generate_name="hdfs-artifact-", entrypoint="artifact-example") as w:
    whalesay = Container(
        name="whalesay",
        command=["sh", "-c"],
        args=["cowsay hello world | tee /tmp/hello_world.txt"],
        image="docker/whalesay:latest",
        outputs=[
            HDFSArtifact(
                name="hello-art",
                path="/tmp/hello_world.txt",
                addresses=[
                    "my-hdfs-namenode-0.my-hdfs-namenode.default.svc.cluster.local:8020",
                    "my-hdfs-namenode-1.my-hdfs-namenode.default.svc.cluster.local:8020",
                ],
                hdfs_path="/tmp/argo/foo",
                hdfs_user="root",
                force=True,
            )
        ],
    )
    print_message = Container(
        name="print-message",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["cat /tmp/message"],
        inputs=[
            HDFSArtifact(
                name="message",
                path="/tmp/message",
                addresses=[
                    "my-hdfs-namenode-0.my-hdfs-namenode.default.svc.cluster.local:8020",
                    "my-hdfs-namenode-1.my-hdfs-namenode.default.svc.cluster.local:8020",
                ],
                hdfs_path="/tmp/argo/foo",
                hdfs_user="root",
                force=True,
            )
        ],
    )

    with Steps(name="artifact-example") as s:
        Step(name="generate-artifact", template=whalesay)
        Step(
            name="consume-artifact",
            template=print_message,
            arguments=[Artifact(name="message", from_="{{steps.generate-artifact.outputs.artifacts.hello-art}}")],
        )
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: hdfs-artifact-
  namespace: default
spec:
  entrypoint: artifact-example
  templates:
  - container:
      args:
      - cowsay hello world | tee /tmp/hello_world.txt
      command:
      - sh
      - -c
      image: docker/whalesay:latest
    name: whalesay
    outputs:
      artifacts:
      - hdfs:
          addresses:
          - my-hdfs-namenode-0.my-hdfs-namenode.default.svc.cluster.local:8020
          - my-hdfs-namenode-1.my-hdfs-namenode.default.svc.cluster.local:8020
          force: true
          hdfsUser: root
          path: /tmp/argo/foo
        name: hello-art
        path: /tmp/hello_world.txt
  - container:
      args:
      - cat /tmp/message
      command:
      - sh
      - -c
      image: alpine:latest
    inputs:
      artifacts:
      - hdfs:
          addresses:
          - my-hdfs-namenode-0.my-hdfs-namenode.default.svc.cluster.local:8020
          - my-hdfs-namenode-1.my-hdfs-namenode.default.svc.cluster.local:8020
          force: true
          hdfsUser: root
          path: /tmp/argo/foo
        name: message
        path: /tmp/message
    name: print-message
  - name: artifact-example
    steps:
    - - name: generate-artifact
        template: whalesay
    - - arguments:
          artifacts:
          - from: '{{steps.generate-artifact.outputs.artifacts.hello-art}}'
            name: message
        name: consume-artifact
        template: print-message
```
