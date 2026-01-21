# Ci Workflowtemplate

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/ci-workflowtemplate.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        DAG,
        Container,
        NoneArchiveStrategy,
        Parameter,
        S3Artifact,
        Task,
        WorkflowTemplate,
        models as m,
    )

    with WorkflowTemplate(
        name="ci",
        arguments=[
            Parameter(name="branch", value="master"),
        ],
        entrypoint="main",
        on_exit="cache-store",
        volume_claim_templates=[
            m.PersistentVolumeClaim(
                metadata=m.ObjectMeta(name="work"),
                spec=m.PersistentVolumeClaimSpec(
                    access_modes=["ReadWriteOnce"],
                    resources=m.VolumeResourceRequirements(
                        requests={
                            "storage": m.Quantity(root="64Mi"),
                        }
                    ),
                ),
            )
        ],
    ) as w:
        cache_restore = Container(
            name="cache-restore",
            image="golang:1.18",
            command=["sh", "-euxc"],
            args=[
                """mkdir -p $(go env GOMODCACHE)
    [ -e /mnt/GOMODCACHE ] && cp -Rf /mnt/GOMODCACHE $(go env GOMODCACHE)
    mkdir -p $(go env GOCACHE)
    [ -e /mnt/GOCACHE ] &&  cp -Rf /mnt/GOCACHE $(go env GOCACHE)
    """,
            ],
            volume_mounts=[
                m.VolumeMount(name="work", mount_path="/go/pkg/mod", sub_path="mod"),
                m.VolumeMount(name="work", mount_path="/root/.cache/go-build", sub_path="cache"),
            ],
            inputs=[
                S3Artifact(
                    name="GOMODCACHE",
                    path="/mnt/GOMODCACHE",
                    optional=True,
                    key="github.com/golang/examples/{{workflow.parameters.branch}}/GOMODCACHE",
                ),
                S3Artifact(
                    name="GOCACHE",
                    path="/mnt/GOCACHE",
                    optional=True,
                    key="github.com/golang/examples/{{workflow.parameters.branch}}/GOCACHE",
                ),
            ],
            working_dir="/go/src/github.com/golang/example",
        )
        clone = Container(
            name="clone",
            image="golang:1.18",
            command=["sh", "-euxc"],
            args=[
                'git clone -v -b "{{workflow.parameters.branch}}" --single-branch --depth 1 https://github.com/golang/example.git .\n',
            ],
            volume_mounts=[
                m.VolumeMount(name="work", mount_path="/go/src/github.com/golang/example", sub_path="src"),
                m.VolumeMount(name="work", mount_path="/go/pkg/mod", sub_path="GOMODCACHE"),
                m.VolumeMount(name="work", mount_path="/root/.cache/go-build", sub_path="GOCACHE"),
            ],
            working_dir="/go/src/github.com/golang/example",
        )
        deps = Container(
            name="deps",
            image="golang:1.18",
            command=["sh", "-xuce"],
            args=["go mod download -x\n"],
            volume_mounts=[
                m.VolumeMount(name="work", mount_path="/go/src/github.com/golang/example", sub_path="src"),
                m.VolumeMount(name="work", mount_path="/go/pkg/mod", sub_path="GOMODCACHE"),
                m.VolumeMount(name="work", mount_path="/root/.cache/go-build", sub_path="GOCACHE"),
            ],
            working_dir="/go/src/github.com/golang/example",
        )
        build = Container(
            name="build",
            image="golang:1.18",
            command=["sh", "-xuce"],
            args=["go build ./...\n"],
            volume_mounts=[
                m.VolumeMount(name="work", mount_path="/go/src/github.com/golang/example", sub_path="src"),
                m.VolumeMount(name="work", mount_path="/go/pkg/mod", sub_path="GOMODCACHE"),
                m.VolumeMount(name="work", mount_path="/root/.cache/go-build", sub_path="GOCACHE"),
            ],
            working_dir="/go/src/github.com/golang/example",
        )
        test = Container(
            name="test",
            image="golang:1.18",
            command=["sh", "-euxc"],
            args=[
                """go install github.com/jstemmer/go-junit-report@latest
    go install github.com/alexec/junit2html@v0.0.2

    trap 'cat test.out | go-junit-report | junit2html > test-report.html' EXIT

    go test -v ./... 2>&1 > test.out
    """,
            ],
            volume_mounts=[
                m.VolumeMount(name="work", mount_path="/go/src/github.com/golang/example", sub_path="src"),
                m.VolumeMount(name="work", mount_path="/go/pkg/mod", sub_path="GOMODCACHE"),
                m.VolumeMount(name="work", mount_path="/root/.cache/go-build", sub_path="GOCACHE"),
            ],
            working_dir="/go/src/github.com/golang/example",
            outputs=[
                S3Artifact(
                    name="test-report",
                    path="/go/src/github.com/golang/example/test-report.html",
                    archive=NoneArchiveStrategy(),
                    key="{{workflow.parameters.branch}}/test-report.html",
                )
            ],
        )

        cache_store = Container(
            name="cache-store",
            image="golang:1.18",
            volume_mounts=[
                m.VolumeMount(name="work", mount_path="/go/pkg/mod", sub_path="GOMODCACHE"),
                m.VolumeMount(name="work", mount_path="/root/.cache/go-build", sub_path="GOCACHE"),
            ],
            outputs=[
                S3Artifact(
                    name="GOMODCACHE",
                    path="/go/pkg/mod",
                    optional=True,
                    key="github.com/golang/examples/{{workflow.parameters.branch}}/GOMODCACHE",
                ),
                S3Artifact(
                    name="GOCACHE",
                    path="/root/.cache/go-build",
                    optional=True,
                    key="github.com/golang/examples/{{workflow.parameters.branch}}/GOCACHE",
                ),
            ],
            working_dir="/go/src/github.com/golang/example",
        )

        with DAG(name="main"):
            cache_restore_task = Task(name="cache-restore", template=cache_restore)
            clone_task = Task(name="clone", template=clone)
            deps_task = Task(name="deps", template=deps, dependencies=["clone", "cache-restore"])
            build_task = Task(name="build", template=build, dependencies=["deps"])
            test_task = Task(name="test", template=test, dependencies=["build"])
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: WorkflowTemplate
    metadata:
      name: ci
    spec:
      entrypoint: main
      onExit: cache-store
      templates:
      - name: cache-restore
        container:
          image: golang:1.18
          workingDir: /go/src/github.com/golang/example
          args:
          - |
            mkdir -p $(go env GOMODCACHE)
            [ -e /mnt/GOMODCACHE ] && cp -Rf /mnt/GOMODCACHE $(go env GOMODCACHE)
            mkdir -p $(go env GOCACHE)
            [ -e /mnt/GOCACHE ] &&  cp -Rf /mnt/GOCACHE $(go env GOCACHE)
          command:
          - sh
          - -euxc
          volumeMounts:
          - name: work
            mountPath: /go/pkg/mod
            subPath: mod
          - name: work
            mountPath: /root/.cache/go-build
            subPath: cache
        inputs:
          artifacts:
          - name: GOMODCACHE
            optional: true
            path: /mnt/GOMODCACHE
            s3:
              key: github.com/golang/examples/{{workflow.parameters.branch}}/GOMODCACHE
          - name: GOCACHE
            optional: true
            path: /mnt/GOCACHE
            s3:
              key: github.com/golang/examples/{{workflow.parameters.branch}}/GOCACHE
      - name: clone
        container:
          image: golang:1.18
          workingDir: /go/src/github.com/golang/example
          args:
          - |
            git clone -v -b "{{workflow.parameters.branch}}" --single-branch --depth 1 https://github.com/golang/example.git .
          command:
          - sh
          - -euxc
          volumeMounts:
          - name: work
            mountPath: /go/src/github.com/golang/example
            subPath: src
          - name: work
            mountPath: /go/pkg/mod
            subPath: GOMODCACHE
          - name: work
            mountPath: /root/.cache/go-build
            subPath: GOCACHE
      - name: deps
        container:
          image: golang:1.18
          workingDir: /go/src/github.com/golang/example
          args:
          - |
            go mod download -x
          command:
          - sh
          - -xuce
          volumeMounts:
          - name: work
            mountPath: /go/src/github.com/golang/example
            subPath: src
          - name: work
            mountPath: /go/pkg/mod
            subPath: GOMODCACHE
          - name: work
            mountPath: /root/.cache/go-build
            subPath: GOCACHE
      - name: build
        container:
          image: golang:1.18
          workingDir: /go/src/github.com/golang/example
          args:
          - |
            go build ./...
          command:
          - sh
          - -xuce
          volumeMounts:
          - name: work
            mountPath: /go/src/github.com/golang/example
            subPath: src
          - name: work
            mountPath: /go/pkg/mod
            subPath: GOMODCACHE
          - name: work
            mountPath: /root/.cache/go-build
            subPath: GOCACHE
      - name: test
        container:
          image: golang:1.18
          workingDir: /go/src/github.com/golang/example
          args:
          - |
            go install github.com/jstemmer/go-junit-report@latest
            go install github.com/alexec/junit2html@v0.0.2

            trap 'cat test.out | go-junit-report | junit2html > test-report.html' EXIT

            go test -v ./... 2>&1 > test.out
          command:
          - sh
          - -euxc
          volumeMounts:
          - name: work
            mountPath: /go/src/github.com/golang/example
            subPath: src
          - name: work
            mountPath: /go/pkg/mod
            subPath: GOMODCACHE
          - name: work
            mountPath: /root/.cache/go-build
            subPath: GOCACHE
        outputs:
          artifacts:
          - name: test-report
            path: /go/src/github.com/golang/example/test-report.html
            archive:
              none: {}
            s3:
              key: '{{workflow.parameters.branch}}/test-report.html'
      - name: cache-store
        container:
          image: golang:1.18
          workingDir: /go/src/github.com/golang/example
          volumeMounts:
          - name: work
            mountPath: /go/pkg/mod
            subPath: GOMODCACHE
          - name: work
            mountPath: /root/.cache/go-build
            subPath: GOCACHE
        outputs:
          artifacts:
          - name: GOMODCACHE
            optional: true
            path: /go/pkg/mod
            s3:
              key: github.com/golang/examples/{{workflow.parameters.branch}}/GOMODCACHE
          - name: GOCACHE
            optional: true
            path: /root/.cache/go-build
            s3:
              key: github.com/golang/examples/{{workflow.parameters.branch}}/GOCACHE
      - name: main
        dag:
          tasks:
          - name: cache-restore
            template: cache-restore
          - name: clone
            template: clone
          - name: deps
            template: deps
            dependencies:
            - clone
            - cache-restore
          - name: build
            template: build
            dependencies:
            - deps
          - name: test
            template: test
            dependencies:
            - build
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
        - name: branch
          value: master
    ```

