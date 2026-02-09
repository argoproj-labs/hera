from hera.workflows import Container, Step, Steps, Workflow
from hera.workflows.models import (
    Arguments,
    Artifact,
    GitArtifact,
    Inputs,
    Item,
    ObjectMeta,
    Parameter,
    PersistentVolumeClaim,
    PersistentVolumeClaimSpec,
    Quantity,
    VolumeMount,
    VolumeResourceRequirements,
)

with Workflow(
    arguments=Arguments(
        parameters=[
            Parameter(
                name="revision",
                value="cfe12d6",
            )
        ],
    ),
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="ci-example-",
    entrypoint="ci-example",
    volume_claim_templates=[
        PersistentVolumeClaim(
            metadata=ObjectMeta(
                name="workdir",
            ),
            spec=PersistentVolumeClaimSpec(
                access_modes=["ReadWriteOnce"],
                resources=VolumeResourceRequirements(
                    requests={
                        "storage": Quantity(
                            root="1Gi",
                        )
                    },
                ),
            ),
        )
    ],
) as w:
    with Steps(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="revision",
                )
            ],
        ),
        name="ci-example",
    ) as invocator:
        Step(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="revision",
                        value="{{inputs.parameters.revision}}",
                    )
                ],
            ),
            name="build",
            template="build-golang-example",
        )
        Step(
            with_items=[
                Item(
                    root={"image": "debian", "tag": "9.1"},
                ),
                Item(
                    root={"image": "alpine", "tag": "3.6"},
                ),
                Item(
                    root={"image": "ubuntu", "tag": "17.10"},
                ),
            ],
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="os-image",
                        value="{{item.image}}:{{item.tag}}",
                    )
                ],
            ),
            name="test",
            template="run-hello",
        )
    Container(
        inputs=Inputs(
            artifacts=[
                Artifact(
                    git=GitArtifact(
                        repo="https://github.com/golang/example.git",
                        revision="{{inputs.parameters.revision}}",
                    ),
                    name="code",
                    path="/go/src/github.com/golang/example",
                )
            ],
            parameters=[
                Parameter(
                    name="revision",
                )
            ],
        ),
        name="build-golang-example",
        args=[" cd /go/src/github.com/golang/example/hello && git status && go build -v . "],
        command=["sh", "-c"],
        image="golang:1.8",
        volume_mounts=[
            VolumeMount(
                mount_path="/go",
                name="workdir",
            )
        ],
    )
    Container(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="os-image",
                )
            ],
        ),
        name="run-hello",
        args=[" uname -a ; cat /etc/os-release ; /go/src/github.com/golang/example/hello/hello "],
        command=["sh", "-c"],
        image="{{inputs.parameters.os-image}}",
        volume_mounts=[
            VolumeMount(
                mount_path="/go",
                name="workdir",
            )
        ],
    )
