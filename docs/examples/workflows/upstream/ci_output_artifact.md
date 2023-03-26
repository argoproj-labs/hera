# Ci Output Artifact

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/ci-output-artifact.yaml).



## Hera

```python
from hera.workflows import (
    Artifact,
    Container,
    GitArtifact,
    Parameter,
    Step,
    Steps,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="ci-output-artifact-",
    entrypoint="ci-example",
    volume_claim_templates=[
        m.PersistentVolumeClaim(
            metadata=m.ObjectMeta(name="workdir"),
            spec=m.PersistentVolumeClaimSpec(
                access_modes=["ReadWriteOnce"],
                resources=m.ResourceRequirements(
                    requests={
                        "storage": m.Quantity(__root__="1Gi"),
                    }
                ),
            ),
        )
    ],
) as w:
    build_golang_example = Container(
        name="build-golang-example",
        image="golang:1.8",
        command=["sh", "-c"],
        args=[" cd /go/src/github.com/golang/example/hello && go build -v . "],
        volume_mounts=[
            m.VolumeMount(name="workdir", mount_path="/go"),
        ],
        inputs=[
            GitArtifact(
                name="code",
                path="/go/src/github.com/golang/example",
                repo="https://github.com/golang/example.git",
                revision="cfe12d6",
            ),
        ],
    )

    run_hello = Container(
        name="run-hello",
        image="{{inputs.parameters.os-image}}",
        command=["sh", "-c"],
        args=[
            " uname -a ; cat " "/etc/os-release ; " "/go/src/github.com/golang/example/hello/hello ",
        ],
        volume_mounts=[
            m.VolumeMount(name="workdir", mount_path="/go"),
        ],
        inputs=[Parameter(name="os-image")],
    )

    release_artifact = Container(
        name="release-artifact",
        image="alpine:3.8",
        volume_mounts=[
            m.VolumeMount(name="workdir", mount_path="/go"),
        ],
        outputs=[
            Artifact(name="release", path="/go"),
        ],
    )

    with Steps(name="ci-example"):
        Step(name="build", template=build_golang_example)
        Step(
            name="test",
            template=run_hello,
            arguments=[Parameter(name="os-image", value="{{item.image}}:{{item.tag}}")],
            with_items=[
                {"image": "debian", "tag": "9.1"},
                {"image": "alpine", "tag": "3.6"},
                {"image": "ubuntu", "tag": "17.10"},
            ],
        )
        Step(name="release", template=release_artifact)
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: ci-output-artifact-
  namespace: default
spec:
  entrypoint: ci-example
  templates:
  - container:
      args:
      - ' cd /go/src/github.com/golang/example/hello && go build -v . '
      command:
      - sh
      - -c
      image: golang:1.8
      volumeMounts:
      - mountPath: /go
        name: workdir
    inputs:
      artifacts:
      - git:
          repo: https://github.com/golang/example.git
          revision: cfe12d6
        name: code
        path: /go/src/github.com/golang/example
    name: build-golang-example
  - container:
      args:
      - ' uname -a ; cat /etc/os-release ; /go/src/github.com/golang/example/hello/hello '
      command:
      - sh
      - -c
      image: '{{inputs.parameters.os-image}}'
      volumeMounts:
      - mountPath: /go
        name: workdir
    inputs:
      parameters:
      - name: os-image
    name: run-hello
  - container:
      image: alpine:3.8
      volumeMounts:
      - mountPath: /go
        name: workdir
    name: release-artifact
    outputs:
      artifacts:
      - name: release
        path: /go
  - name: ci-example
    steps:
    - - name: build
        template: build-golang-example
    - - arguments:
          parameters:
          - name: os-image
            value: '{{item.image}}:{{item.tag}}'
        name: test
        template: run-hello
        withItems:
        - image: debian
          tag: '9.1'
        - image: alpine
          tag: '3.6'
        - image: ubuntu
          tag: '17.10'
    - - name: release
        template: release-artifact
  volumeClaimTemplates:
  - metadata:
      name: workdir
    spec:
      accessModes:
      - ReadWriteOnce
      resources:
        requests:
          storage: 1Gi
```
