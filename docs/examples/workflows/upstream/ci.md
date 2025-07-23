# Ci

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/ci.yaml).




=== "Hera"

    ```python linenums="1"
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
                                __root__="1Gi",
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
                        __root__={"image": "debian", "tag": "9.1"},
                    ),
                    Item(
                        __root__={"image": "alpine", "tag": "3.6"},
                    ),
                    Item(
                        __root__={"image": "ubuntu", "tag": "17.10"},
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
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: ci-example-
    spec:
      entrypoint: ci-example
      templates:
      - name: ci-example
        steps:
        - - name: build
            template: build-golang-example
            arguments:
              parameters:
              - name: revision
                value: '{{inputs.parameters.revision}}'
        - - name: test
            template: run-hello
            withItems:
            - image: debian
              tag: '9.1'
            - image: alpine
              tag: '3.6'
            - image: ubuntu
              tag: '17.10'
            arguments:
              parameters:
              - name: os-image
                value: '{{item.image}}:{{item.tag}}'
        inputs:
          parameters:
          - name: revision
      - name: build-golang-example
        container:
          image: golang:1.8
          args:
          - ' cd /go/src/github.com/golang/example/hello && git status && go build -v
            . '
          command:
          - sh
          - -c
          volumeMounts:
          - name: workdir
            mountPath: /go
        inputs:
          artifacts:
          - name: code
            path: /go/src/github.com/golang/example
            git:
              repo: https://github.com/golang/example.git
              revision: '{{inputs.parameters.revision}}'
          parameters:
          - name: revision
      - name: run-hello
        container:
          image: '{{inputs.parameters.os-image}}'
          args:
          - ' uname -a ; cat /etc/os-release ; /go/src/github.com/golang/example/hello/hello '
          command:
          - sh
          - -c
          volumeMounts:
          - name: workdir
            mountPath: /go
        inputs:
          parameters:
          - name: os-image
      volumeClaimTemplates:
      - metadata:
          name: workdir
        spec:
          accessModes:
          - ReadWriteOnce
          resources:
            requests:
              storage: 1Gi
      arguments:
        parameters:
        - name: revision
          value: cfe12d6
    ```

