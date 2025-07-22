from hera.workflows import Container, Step, Steps, Workflow
from hera.workflows.models import Arguments, HTTPGetAction, Inputs, Parameter, Probe

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="daemon-step-",
    entrypoint="daemon-example",
) as w:
    with Steps(
        name="daemon-example",
    ) as invocator:
        Step(
            name="influx",
            template="influxdb",
        )
        Step(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="cmd",
                        value="curl -XPOST 'http://{{steps.influx.ip}}:8086/query' --data-urlencode \"q=CREATE DATABASE mydb\"",
                    )
                ],
            ),
            name="init-database",
            template="influxdb-client",
        )
        with invocator.parallel():
            Step(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="cmd",
                            value="for i in $(seq 1 20); do curl -XPOST 'http://{{steps.influx.ip}}:8086/write?db=mydb' -d \"cpu,host=server01,region=uswest load=$i\" ; sleep .5 ; done",
                        )
                    ],
                ),
                name="producer-1",
                template="influxdb-client",
            )
            Step(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="cmd",
                            value="for i in $(seq 1 20); do curl -XPOST 'http://{{steps.influx.ip}}:8086/write?db=mydb' -d \"cpu,host=server02,region=uswest load=$((RANDOM % 100))\" ; sleep .5 ; done",
                        )
                    ],
                ),
                name="producer-2",
                template="influxdb-client",
            )
            Step(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="cmd",
                            value="curl -XPOST 'http://{{steps.influx.ip}}:8086/write?db=mydb' -d 'cpu,host=server03,region=useast load=15.4'",
                        )
                    ],
                ),
                name="producer-3",
                template="influxdb-client",
            )
        Step(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="cmd",
                        value='curl --silent -G http://{{steps.influx.ip}}:8086/query?pretty=true --data-urlencode "db=mydb" --data-urlencode "q=SELECT * FROM cpu"',
                    )
                ],
            ),
            name="consumer",
            template="influxdb-client",
        )
    Container(
        daemon=True,
        name="influxdb",
        image="influxdb:1.2",
        readiness_probe=Probe(
            http_get=HTTPGetAction(
                path="/ping",
                port=8086,
            ),
            initial_delay_seconds=5,
            timeout_seconds=1,
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
        command=["sh", "-c"],
        image="appropriate/curl:latest",
    )
