# Influxdb Ci

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/influxdb-ci.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow
    from hera.workflows.models import (
        Arguments,
        Artifact,
        GitArtifact,
        HTTPGetAction,
        Inputs,
        Outputs,
        Parameter,
        Probe,
        Quantity,
        ResourceRequirements,
    )

    with Workflow(
        arguments=Arguments(
            parameters=[
                Parameter(
                    name="repo",
                    value="https://github.com/influxdata/influxdb.git",
                ),
                Parameter(
                    name="revision",
                    value="1.6",
                ),
            ],
        ),
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="influxdb-ci-",
        entrypoint="influxdb-ci",
    ) as w:
        with Steps(
            name="influxdb-ci",
        ) as invocator:
            Step(
                name="checkout",
                template="checkout",
            )
            with invocator.parallel():
                Step(
                    arguments=Arguments(
                        artifacts=[
                            Artifact(
                                from_="{{steps.checkout.outputs.artifacts.source}}",
                                name="source",
                            )
                        ],
                    ),
                    name="build",
                    template="build",
                )
                Step(
                    arguments=Arguments(
                        artifacts=[
                            Artifact(
                                from_="{{steps.checkout.outputs.artifacts.source}}",
                                name="source",
                            )
                        ],
                    ),
                    name="test-unit",
                    template="test-unit",
                )
            with invocator.parallel():
                Step(
                    arguments=Arguments(
                        artifacts=[
                            Artifact(
                                from_="{{steps.checkout.outputs.artifacts.source}}",
                                name="source",
                            )
                        ],
                    ),
                    name="test-cov",
                    template="test-cov",
                )
                Step(
                    arguments=Arguments(
                        artifacts=[
                            Artifact(
                                from_="{{steps.build.outputs.artifacts.influxd}}",
                                name="influxd",
                            )
                        ],
                    ),
                    name="test-e2e",
                    template="test-e2e",
                )
        Container(
            inputs=Inputs(
                artifacts=[
                    Artifact(
                        git=GitArtifact(
                            repo="{{workflow.parameters.repo}}",
                            revision="{{workflow.parameters.revision}}",
                        ),
                        name="source",
                        path="/src",
                    )
                ],
            ),
            name="checkout",
            outputs=Outputs(
                artifacts=[
                    Artifact(
                        name="source",
                        path="/src",
                    )
                ],
            ),
            args=["cd /src && git status && ls -l"],
            command=["/bin/sh", "-c"],
            image="golang:1.9.2",
        )
        Container(
            inputs=Inputs(
                artifacts=[
                    Artifact(
                        name="source",
                        path="/go/src/github.com/influxdata/influxdb",
                    )
                ],
            ),
            name="build",
            outputs=Outputs(
                artifacts=[
                    Artifact(
                        name="influxd",
                        path="/go/bin",
                    )
                ],
            ),
            args=[
                " cd /go/src/github.com/influxdata/influxdb && go get github.com/golang/dep/cmd/dep && dep ensure -vendor-only && go install -v ./... "
            ],
            command=["/bin/sh", "-c"],
            image="golang:1.9.2",
            resources=ResourceRequirements(
                requests={
                    "memory": Quantity(
                        __root__="1024Mi",
                    ),
                    "cpu": Quantity(
                        __root__="200m",
                    ),
                },
            ),
        )
        Container(
            inputs=Inputs(
                artifacts=[
                    Artifact(
                        name="source",
                        path="/go/src/github.com/influxdata/influxdb",
                    )
                ],
            ),
            name="test-unit",
            args=[
                " cd /go/src/github.com/influxdata/influxdb && go get github.com/golang/dep/cmd/dep && dep ensure -vendor-only && go test -parallel=1 ./... "
            ],
            command=["/bin/sh", "-c"],
            image="golang:1.9.2",
        )
        with Steps(
            inputs=Inputs(
                artifacts=[
                    Artifact(
                        name="source",
                    )
                ],
            ),
            name="test-cov",
        ) as invocator:
            with invocator.parallel():
                Step(
                    arguments=Arguments(
                        artifacts=[
                            Artifact(
                                from_="{{inputs.artifacts.source}}",
                                name="source",
                            )
                        ],
                        parameters=[
                            Parameter(
                                name="package",
                                value="query",
                            )
                        ],
                    ),
                    name="test-cov-query",
                    template="test-cov-base",
                )
                Step(
                    arguments=Arguments(
                        artifacts=[
                            Artifact(
                                from_="{{inputs.artifacts.source}}",
                                name="source",
                            )
                        ],
                        parameters=[
                            Parameter(
                                name="package",
                                value="tsdb/engine/tsm1",
                            )
                        ],
                    ),
                    name="test-cov-tsm1",
                    template="test-cov-base",
                )
        Container(
            inputs=Inputs(
                artifacts=[
                    Artifact(
                        name="source",
                        path="/go/src/github.com/influxdata/influxdb",
                    )
                ],
                parameters=[
                    Parameter(
                        name="package",
                    )
                ],
            ),
            name="test-cov-base",
            outputs=Outputs(
                artifacts=[
                    Artifact(
                        name="covreport",
                        path="/tmp/index.html",
                    )
                ],
            ),
            args=[
                " cd /go/src/github.com/influxdata/influxdb && go get github.com/golang/dep/cmd/dep && dep ensure -vendor-only && go test -v -coverprofile /tmp/cov.out ./{{inputs.parameters.package}} && go tool cover -html=/tmp/cov.out -o /tmp/index.html "
            ],
            command=["/bin/sh", "-c"],
            image="golang:1.9.2",
            resources=ResourceRequirements(
                requests={
                    "memory": Quantity(
                        __root__="4096Mi",
                    ),
                    "cpu": Quantity(
                        __root__="200m",
                    ),
                },
            ),
        )
        with Steps(
            inputs=Inputs(
                artifacts=[
                    Artifact(
                        name="influxd",
                    )
                ],
            ),
            name="test-e2e",
        ) as invocator:
            Step(
                arguments=Arguments(
                    artifacts=[
                        Artifact(
                            from_="{{inputs.artifacts.influxd}}",
                            name="influxd",
                        )
                    ],
                ),
                name="influxdb-server",
                template="influxdb-server",
            )
            Step(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="cmd",
                            value="curl -XPOST 'http://{{steps.influxdb-server.ip}}:8086/query' --data-urlencode \"q=CREATE DATABASE mydb\"",
                        )
                    ],
                ),
                name="initdb",
                template="influxdb-client",
            )
            with invocator.parallel():
                Step(
                    arguments=Arguments(
                        parameters=[
                            Parameter(
                                name="cmd",
                                value="for i in $(seq 1 20); do curl -XPOST 'http://{{steps.influxdb-server.ip}}:8086/write?db=mydb' -d \"cpu,host=server01,region=uswest load=$i\" ; sleep .5 ; done",
                            )
                        ],
                    ),
                    name="producer1",
                    template="influxdb-client",
                )
                Step(
                    arguments=Arguments(
                        parameters=[
                            Parameter(
                                name="cmd",
                                value="for i in $(seq 1 20); do curl -XPOST 'http://{{steps.influxdb-server.ip}}:8086/write?db=mydb' -d \"cpu,host=server02,region=uswest load=$((RANDOM % 100))\" ; sleep .5 ; done",
                            )
                        ],
                    ),
                    name="producer2",
                    template="influxdb-client",
                )
                Step(
                    arguments=Arguments(
                        parameters=[
                            Parameter(
                                name="cmd",
                                value="curl -XPOST 'http://{{steps.influxdb-server.ip}}:8086/write?db=mydb' -d 'cpu,host=server03,region=useast load=15.4'",
                            )
                        ],
                    ),
                    name="producer3",
                    template="influxdb-client",
                )
                Step(
                    arguments=Arguments(
                        parameters=[
                            Parameter(
                                name="cmd",
                                value='curl --silent -G http://{{steps.influxdb-server.ip}}:8086/query?pretty=true --data-urlencode "db=mydb" --data-urlencode "q=SELECT * FROM cpu"',
                            )
                        ],
                    ),
                    name="consumer",
                    template="influxdb-client",
                )
        Container(
            daemon=True,
            inputs=Inputs(
                artifacts=[
                    Artifact(
                        name="influxd",
                        path="/app",
                    )
                ],
            ),
            name="influxdb-server",
            outputs=Outputs(
                artifacts=[
                    Artifact(
                        name="data",
                        path="/var/lib/influxdb/data",
                    )
                ],
            ),
            args=["chmod +x /app/influxd && /app/influxd"],
            command=["/bin/sh", "-c"],
            image="debian:9.4",
            readiness_probe=Probe(
                http_get=HTTPGetAction(
                    path="/ping",
                    port=8086,
                ),
                initial_delay_seconds=5,
                timeout_seconds=1,
            ),
            resources=ResourceRequirements(
                requests={
                    "memory": Quantity(
                        __root__="512Mi",
                    ),
                    "cpu": Quantity(
                        __root__="250m",
                    ),
                },
            ),
        )
        Container(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="cmd",
                    )
                ],
            ),
            name="influxdb-client",
            args=["{{inputs.parameters.cmd}}"],
            command=["/bin/sh", "-c"],
            image="appropriate/curl:latest",
            resources=ResourceRequirements(
                requests={
                    "memory": Quantity(
                        __root__="32Mi",
                    ),
                    "cpu": Quantity(
                        __root__="100m",
                    ),
                },
            ),
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: influxdb-ci-
    spec:
      entrypoint: influxdb-ci
      templates:
      - name: influxdb-ci
        steps:
        - - name: checkout
            template: checkout
        - - name: build
            template: build
            arguments:
              artifacts:
              - name: source
                from: '{{steps.checkout.outputs.artifacts.source}}'
          - name: test-unit
            template: test-unit
            arguments:
              artifacts:
              - name: source
                from: '{{steps.checkout.outputs.artifacts.source}}'
        - - name: test-cov
            template: test-cov
            arguments:
              artifacts:
              - name: source
                from: '{{steps.checkout.outputs.artifacts.source}}'
          - name: test-e2e
            template: test-e2e
            arguments:
              artifacts:
              - name: influxd
                from: '{{steps.build.outputs.artifacts.influxd}}'
      - name: checkout
        container:
          image: golang:1.9.2
          args:
          - cd /src && git status && ls -l
          command:
          - /bin/sh
          - -c
        inputs:
          artifacts:
          - name: source
            path: /src
            git:
              repo: '{{workflow.parameters.repo}}'
              revision: '{{workflow.parameters.revision}}'
        outputs:
          artifacts:
          - name: source
            path: /src
      - name: build
        container:
          image: golang:1.9.2
          args:
          - ' cd /go/src/github.com/influxdata/influxdb && go get github.com/golang/dep/cmd/dep
            && dep ensure -vendor-only && go install -v ./... '
          command:
          - /bin/sh
          - -c
          resources:
            requests:
              cpu: 200m
              memory: 1024Mi
        inputs:
          artifacts:
          - name: source
            path: /go/src/github.com/influxdata/influxdb
        outputs:
          artifacts:
          - name: influxd
            path: /go/bin
      - name: test-unit
        container:
          image: golang:1.9.2
          args:
          - ' cd /go/src/github.com/influxdata/influxdb && go get github.com/golang/dep/cmd/dep
            && dep ensure -vendor-only && go test -parallel=1 ./... '
          command:
          - /bin/sh
          - -c
        inputs:
          artifacts:
          - name: source
            path: /go/src/github.com/influxdata/influxdb
      - name: test-cov
        steps:
        - - name: test-cov-query
            template: test-cov-base
            arguments:
              artifacts:
              - name: source
                from: '{{inputs.artifacts.source}}'
              parameters:
              - name: package
                value: query
          - name: test-cov-tsm1
            template: test-cov-base
            arguments:
              artifacts:
              - name: source
                from: '{{inputs.artifacts.source}}'
              parameters:
              - name: package
                value: tsdb/engine/tsm1
        inputs:
          artifacts:
          - name: source
      - name: test-cov-base
        container:
          image: golang:1.9.2
          args:
          - ' cd /go/src/github.com/influxdata/influxdb && go get github.com/golang/dep/cmd/dep
            && dep ensure -vendor-only && go test -v -coverprofile /tmp/cov.out ./{{inputs.parameters.package}}
            && go tool cover -html=/tmp/cov.out -o /tmp/index.html '
          command:
          - /bin/sh
          - -c
          resources:
            requests:
              cpu: 200m
              memory: 4096Mi
        inputs:
          artifacts:
          - name: source
            path: /go/src/github.com/influxdata/influxdb
          parameters:
          - name: package
        outputs:
          artifacts:
          - name: covreport
            path: /tmp/index.html
      - name: test-e2e
        steps:
        - - name: influxdb-server
            template: influxdb-server
            arguments:
              artifacts:
              - name: influxd
                from: '{{inputs.artifacts.influxd}}'
        - - name: initdb
            template: influxdb-client
            arguments:
              parameters:
              - name: cmd
                value: curl -XPOST 'http://{{steps.influxdb-server.ip}}:8086/query' --data-urlencode
                  "q=CREATE DATABASE mydb"
        - - name: producer1
            template: influxdb-client
            arguments:
              parameters:
              - name: cmd
                value: for i in $(seq 1 20); do curl -XPOST 'http://{{steps.influxdb-server.ip}}:8086/write?db=mydb'
                  -d "cpu,host=server01,region=uswest load=$i" ; sleep .5 ; done
          - name: producer2
            template: influxdb-client
            arguments:
              parameters:
              - name: cmd
                value: for i in $(seq 1 20); do curl -XPOST 'http://{{steps.influxdb-server.ip}}:8086/write?db=mydb'
                  -d "cpu,host=server02,region=uswest load=$((RANDOM % 100))" ; sleep
                  .5 ; done
          - name: producer3
            template: influxdb-client
            arguments:
              parameters:
              - name: cmd
                value: curl -XPOST 'http://{{steps.influxdb-server.ip}}:8086/write?db=mydb'
                  -d 'cpu,host=server03,region=useast load=15.4'
          - name: consumer
            template: influxdb-client
            arguments:
              parameters:
              - name: cmd
                value: curl --silent -G http://{{steps.influxdb-server.ip}}:8086/query?pretty=true
                  --data-urlencode "db=mydb" --data-urlencode "q=SELECT * FROM cpu"
        inputs:
          artifacts:
          - name: influxd
      - name: influxdb-server
        daemon: true
        container:
          image: debian:9.4
          args:
          - chmod +x /app/influxd && /app/influxd
          command:
          - /bin/sh
          - -c
          readinessProbe:
            initialDelaySeconds: 5
            timeoutSeconds: 1
            httpGet:
              path: /ping
              port: 8086
          resources:
            requests:
              cpu: 250m
              memory: 512Mi
        inputs:
          artifacts:
          - name: influxd
            path: /app
        outputs:
          artifacts:
          - name: data
            path: /var/lib/influxdb/data
      - name: influxdb-client
        container:
          image: appropriate/curl:latest
          args:
          - '{{inputs.parameters.cmd}}'
          command:
          - /bin/sh
          - -c
          resources:
            requests:
              cpu: 100m
              memory: 32Mi
        inputs:
          parameters:
          - name: cmd
      arguments:
        parameters:
        - name: repo
          value: https://github.com/influxdata/influxdb.git
        - name: revision
          value: '1.6'
    ```

