from hera.workflows import DAG, Container, Task, Workflow
from hera.workflows.models import (
    Arguments,
    HTTPGetAction,
    Inputs,
    IntOrString,
    Mutex,
    Parameter,
    Probe,
    RetryStrategy,
    Sequence,
    Synchronization,
)

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="dag-daemon-retry-",
    entrypoint="main",
) as w:
    with DAG(
        name="main",
    ) as invocator:
        Task(
            name="server",
            template="server",
        )
        Task(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="server-ip",
                        value="{{tasks.server.ip}}",
                    )
                ],
            ),
            name="client",
            template="client",
            with_sequence=Sequence(
                count=IntOrString(
                    root="10",
                ),
            ),
            depends="server",
        )
    Container(
        daemon=True,
        name="server",
        retry_strategy=RetryStrategy(
            limit=IntOrString(
                root="10",
            ),
        ),
        args=["-g", "daemon off;"],
        command=["nginx"],
        image="nginx:latest",
        readiness_probe=Probe(
            http_get=HTTPGetAction(
                path="/",
                port=80,
            ),
            initial_delay_seconds=2,
            timeout_seconds=1,
        ),
    )
    Container(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="server-ip",
                )
            ],
        ),
        name="client",
        synchronization=Synchronization(
            mutex=Mutex(
                name="client-{{workflow.uid}}",
            ),
        ),
        args=[
            "echo curl --silent -G http://{{inputs.parameters.server-ip}}:80/ && curl --silent -G http://{{inputs.parameters.server-ip}}:80/"
        ],
        command=["/bin/sh", "-c"],
        image="appropriate/curl:latest",
    )
