from hera.workflows import (
    Container,
    Steps,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="synchronization-tmpl-level-",
    entrypoint="synchronization-tmpl-level-example",
) as w:
    acquire_lock = Container(
        name="acquire-lock",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["sleep 10; echo acquired lock"],
        synchronization=m.Synchronization(
            semaphore=m.SemaphoreRef(config_map_key_ref=m.ConfigMapKeySelector(name="my-config", key="template"))
        ),
    )
    with Steps(name="synchronization-tmpl-level-example") as s:
        acquire_lock(
            name="synchronization-acquire-lock",
            arguments={"seconds": "{{item}}"},
            with_param='["1","2","3","4","5"]',
        )
