from hera.workflows import (
    Container,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="synchronization-wf-level-",
    entrypoint="whalesay",
    synchronization=m.Synchronization(
        semaphore=m.SemaphoreRef(
            config_map_key_ref=m.ConfigMapKeySelector(
                name="my-config",
                key="workflow",
            )
        )
    ),
) as w:
    whalesay = Container(
        name="whalesay",
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=["hello world"],
    )
