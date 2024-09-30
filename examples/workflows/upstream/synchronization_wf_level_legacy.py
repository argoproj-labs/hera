from hera.workflows import (
    Container,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="synchronization-wf-level-",
    entrypoint="hello-world",
    synchronization=m.Synchronization(
        semaphore=m.SemaphoreRef(
            config_map_key_ref=m.ConfigMapKeySelector(
                name="my-config",
                key="workflow",
            )
        )
    ),
) as w:
    hello_world = Container(
        name="hello-world",
        image="busybox",
        command=["echo"],
        args=["hello world"],
    )
