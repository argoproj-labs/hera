# Buildkit Template

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/buildkit-template.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, Task, WorkflowTemplate
    from hera.workflows.models import (
        Arguments,
        EnvVar,
        ExecAction,
        Inputs,
        ObjectMeta,
        Parameter,
        PersistentVolumeClaim,
        PersistentVolumeClaimSpec,
        Probe,
        Quantity,
        SecretVolumeSource,
        Volume,
        VolumeMount,
        VolumeResourceRequirements,
    )

    with WorkflowTemplate(
        arguments=Arguments(
            parameters=[
                Parameter(
                    name="repo",
                    value="https://github.com/argoproj/argo-workflows",
                ),
                Parameter(
                    name="branch",
                    value="master",
                ),
                Parameter(
                    name="path",
                    value="test/e2e/images/argosay/v2",
                ),
                Parameter(
                    name="image",
                    value="alexcollinsintuit/argosay:v2",
                ),
            ],
        ),
        api_version="argoproj.io/v1alpha1",
        kind="WorkflowTemplate",
        name="buildkit",
        entrypoint="main",
        volume_claim_templates=[
            PersistentVolumeClaim(
                metadata=ObjectMeta(
                    name="work",
                ),
                spec=PersistentVolumeClaimSpec(
                    access_modes=["ReadWriteOnce"],
                    resources=VolumeResourceRequirements(
                        requests={
                            "storage": Quantity(
                                __root__="64Mi",
                            )
                        },
                    ),
                ),
            )
        ],
    ) as w:
        with DAG(
            name="main",
        ) as invocator:
            Task(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="repo",
                            value="{{workflow.parameters.repo}}",
                        ),
                        Parameter(
                            name="branch",
                            value="{{workflow.parameters.branch}}",
                        ),
                    ],
                ),
                name="clone",
                template="clone",
            )
            Task(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="path",
                            value="{{workflow.parameters.path}}",
                        )
                    ],
                ),
                name="build",
                template="build",
                depends="clone",
            )
            Task(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="path",
                            value="{{workflow.parameters.path}}",
                        ),
                        Parameter(
                            name="image",
                            value="{{workflow.parameters.image}}",
                        ),
                    ],
                ),
                name="image",
                template="image",
                depends="build",
            )
        Container(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="repo",
                    ),
                    Parameter(
                        name="branch",
                    ),
                ],
            ),
            name="clone",
            args=[
                "clone",
                "--depth",
                "1",
                "--branch",
                "{{inputs.parameters.branch}}",
                "--single-branch",
                "{{inputs.parameters.repo}}",
                ".",
            ],
            image="alpine/git:v2.26.2",
            volume_mounts=[
                VolumeMount(
                    mount_path="/work",
                    name="work",
                )
            ],
            working_dir="/work",
        )
        Container(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="path",
                    )
                ],
            ),
            name="build",
            args=["build", "-v", "-o", "argosay", "./..."],
            command=["go"],
            env=[
                EnvVar(
                    name="GO111MODULE",
                    value="off",
                )
            ],
            image="golang:1.13",
            volume_mounts=[
                VolumeMount(
                    mount_path="/work",
                    name="work",
                )
            ],
            working_dir="/work/{{inputs.parameters.path}}",
        )
        Container(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="path",
                    ),
                    Parameter(
                        name="image",
                    ),
                ],
            ),
            name="image",
            volumes=[
                Volume(
                    name="docker-config",
                    secret=SecretVolumeSource(
                        secret_name="docker-config",
                    ),
                )
            ],
            args=[
                "build",
                "--frontend",
                "dockerfile.v0",
                "--local",
                "context=.",
                "--local",
                "dockerfile=.",
                "--output",
                "type=image,name=docker.io/{{inputs.parameters.image}},push=true",
            ],
            command=["buildctl-daemonless.sh"],
            env=[
                EnvVar(
                    name="BUILDKITD_FLAGS",
                    value="--oci-worker-no-process-sandbox",
                ),
                EnvVar(
                    name="DOCKER_CONFIG",
                    value="/.docker",
                ),
            ],
            image="moby/buildkit:v0.9.3-rootless",
            readiness_probe=Probe(
                exec=ExecAction(
                    command=["sh", "-c", "buildctl debug workers"],
                ),
            ),
            volume_mounts=[
                VolumeMount(
                    mount_path="/work",
                    name="work",
                ),
                VolumeMount(
                    mount_path="/.docker",
                    name="docker-config",
                ),
            ],
            working_dir="/work/{{inputs.parameters.path}}",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: WorkflowTemplate
    metadata:
      name: buildkit
    spec:
      entrypoint: main
      templates:
      - name: main
        dag:
          tasks:
          - name: clone
            template: clone
            arguments:
              parameters:
              - name: repo
                value: '{{workflow.parameters.repo}}'
              - name: branch
                value: '{{workflow.parameters.branch}}'
          - name: build
            depends: clone
            template: build
            arguments:
              parameters:
              - name: path
                value: '{{workflow.parameters.path}}'
          - name: image
            depends: build
            template: image
            arguments:
              parameters:
              - name: path
                value: '{{workflow.parameters.path}}'
              - name: image
                value: '{{workflow.parameters.image}}'
      - name: clone
        container:
          image: alpine/git:v2.26.2
          workingDir: /work
          args:
          - clone
          - --depth
          - '1'
          - --branch
          - '{{inputs.parameters.branch}}'
          - --single-branch
          - '{{inputs.parameters.repo}}'
          - .
          volumeMounts:
          - name: work
            mountPath: /work
        inputs:
          parameters:
          - name: repo
          - name: branch
      - name: build
        container:
          image: golang:1.13
          workingDir: /work/{{inputs.parameters.path}}
          args:
          - build
          - -v
          - -o
          - argosay
          - ./...
          command:
          - go
          env:
          - name: GO111MODULE
            value: 'off'
          volumeMounts:
          - name: work
            mountPath: /work
        inputs:
          parameters:
          - name: path
      - name: image
        volumes:
        - name: docker-config
          secret:
            secretName: docker-config
        container:
          image: moby/buildkit:v0.9.3-rootless
          workingDir: /work/{{inputs.parameters.path}}
          args:
          - build
          - --frontend
          - dockerfile.v0
          - --local
          - context=.
          - --local
          - dockerfile=.
          - --output
          - type=image,name=docker.io/{{inputs.parameters.image}},push=true
          command:
          - buildctl-daemonless.sh
          env:
          - name: BUILDKITD_FLAGS
            value: --oci-worker-no-process-sandbox
          - name: DOCKER_CONFIG
            value: /.docker
          volumeMounts:
          - name: work
            mountPath: /work
          - name: docker-config
            mountPath: /.docker
          readinessProbe:
            exec:
              command:
              - sh
              - -c
              - buildctl debug workers
        inputs:
          parameters:
          - name: path
          - name: image
      volumeClaimTemplates:
      - metadata:
          name: work
        spec:
          accessModes:
          - ReadWriteOnce
          resources:
            requests:
              storage: 64Mi
      arguments:
        parameters:
        - name: repo
          value: https://github.com/argoproj/argo-workflows
        - name: branch
          value: master
        - name: path
          value: test/e2e/images/argosay/v2
        - name: image
          value: alexcollinsintuit/argosay:v2
    ```

