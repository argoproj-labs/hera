from hera.workflows import Container, Step, Steps, Workflow
from hera.workflows.models import Arguments, Mutex, Parameter, Synchronization

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="synchronization-db-tmpl-level-mutex-",
    entrypoint="synchronization-db-tmpl-level-mutex-example",
) as w:
    with Steps(
        name="synchronization-db-tmpl-level-mutex-example",
    ) as invocator:
        with invocator.parallel():
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
                name="synchronization-acquire-lock1",
                template="acquire-lock-1",
            )
    Container(
        name="acquire-lock",
        synchronization=Synchronization(
            mutexes=[
                Mutex(
                    name="welcome",
                )
            ],
        ),
        args=["sleep 20; echo acquired lock"],
        command=["sh", "-c"],
        image="alpine:latest",
    )
    Container(
        name="acquire-lock-1",
        synchronization=Synchronization(
            mutexes=[
                Mutex(
                    name="test",
                )
            ],
        ),
        args=["sleep 50; echo acquired lock"],
        command=["sh", "-c"],
        image="alpine:latest",
    )
