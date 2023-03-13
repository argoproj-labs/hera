"""
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: ci-output-artifact-
spec:
  entrypoint: ci-example
  # a temporary volume, named workdir, will be used as a working
  # directory for this workflow. This volume is passed around
  # from step to step.
  volumeClaimTemplates:
  - metadata:
      name: workdir
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi

  templates:
  - name: ci-example
    steps:
    - - name: build
        template: build-golang-example
    # the test step expands into three parallel steps running
    # different operating system images. each mounts the workdir
    # and runs the compiled binary from the build step.
    - - name: test
        template: run-hello
        arguments:
          parameters:
          - name: os-image
            value: "{{item.image}}:{{item.tag}}"
        withItems:
        - { image: 'debian', tag: '9.1' }
        - { image: 'alpine', tag: '3.6' }
        - { image: 'ubuntu', tag: '17.10' }
    - - name: release
        template: release-artifact


  - name: build-golang-example
    inputs:
      artifacts:
      - name: code
        path: /go/src/github.com/golang/example
        git:
          repo: https://github.com/golang/example.git
          revision: cfe12d6
    container:
      image: golang:1.8
      command: [sh, -c]
      args: ["
        cd /go/src/github.com/golang/example/hello &&
        go build -v .
      "]
      volumeMounts:
      - name: workdir
        mountPath: /go
  - name: run-hello
    inputs:
      parameters:
      - name: os-image
    container:
      image: "{{inputs.parameters.os-image}}"
      command: [sh, -c]
      args: ["
        uname -a ;
        cat /etc/os-release ;
        /go/src/github.com/golang/example/hello/hello
      "]
      volumeMounts:
      - name: workdir
        mountPath: /go
  - name: release-artifact
    container:
      image: alpine:3.8
      volumeMounts:
      - name: workdir
        mountPath: /go
    outputs:
      artifacts:
      - name: release
        path: /go
"""
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
                m.Item(__root__={"image": "debian", "tag": "9.1"}),
                m.Item(__root__={"image": "alpine", "tag": "3.6"}),
                m.Item(__root__={"image": "ubuntu", "tag": "17.10"}),
            ],
        )
        Step(name="release", template=release_artifact)
