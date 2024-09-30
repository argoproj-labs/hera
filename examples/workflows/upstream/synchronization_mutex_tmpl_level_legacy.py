from hera.workflows import (
    Container,
    Steps,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="synchronization-tmpl-level-mutex-",
    entrypoint="synchronization-tmpl-level-mutex-example",
) as w:
    acquire_lock = Container(
        name="acquire-lock",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["sleep 20; echo acquired lock"],
        synchronization=m.Synchronization(mutex=m.Mutex(name="welcome")),
    )
    acquire_lock_1 = Container(
        name="acquire-lock-1",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["sleep 50; echo acquired lock"],
        synchronization=m.Synchronization(mutex=m.Mutex(name="test")),
    )
    with Steps(name="synchronization-tmpl-level-mutex-example") as s:
        with s.parallel():
            acquire_lock(
                name="synchronization-acquire-lock",
                arguments={"seconds": "{{item}}"},
                with_param='["1","2","3","4","5"]',
            )

            acquire_lock_1(
                name="synchronization-acquire-lock1",
                arguments={"seconds": "{{item}}"},
                with_param='["1","2","3","4","5"]',
            )
