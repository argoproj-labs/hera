from hera.workflows import Container, Step, Steps, Workflow
from hera.workflows.models import Arguments, Parameter, SemaphoreRef, SyncDatabaseRef, Synchronization

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="synchronization-db-tmpl-level-",
    entrypoint="synchronization-db-tmpl-level-example",
) as w:
    with Steps(
        name="synchronization-db-tmpl-level-example",
    ) as invocator:
        Step(
            with_param='["1","2","3","4","5"]',
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="seconds",
                        value="{{item}}",
                    )
                ],
            ),
            name="synchronization-acquire-lock",
            template="acquire-lock",
        )
    Container(
        name="acquire-lock",
        synchronization=Synchronization(
            semaphores=[
                SemaphoreRef(
                    database=SyncDatabaseRef(key="template"),
                )
            ]
        ),
        args=["sleep 10; echo acquired lock"],
        command=["sh", "-c"],
        image="alpine:latest",
    )
