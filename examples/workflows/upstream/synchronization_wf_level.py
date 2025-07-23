from hera.workflows import Container, Workflow
from hera.workflows.models import ConfigMapKeySelector, SemaphoreRef, Synchronization

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="synchronization-wf-level-",
    entrypoint="hello-world",
    synchronization=Synchronization(
        semaphores=[
            SemaphoreRef(
                config_map_key_ref=ConfigMapKeySelector(
                    key="workflow",
                    name="my-config",
                ),
            )
        ],
    ),
) as w:
    Container(
        name="hello-world",
        args=["hello world"],
        command=["echo"],
        image="busybox",
    )
