from hera.workflows import Container, Workflow
from hera.workflows.models import SemaphoreRef, Synchronization

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="synchronization-db-wf-level-",
    entrypoint="hello-world",
    synchronization=Synchronization(
        semaphores=[SemaphoreRef()],
    ),
) as w:
    Container(
        name="hello-world",
        args=["hello world"],
        command=["echo"],
        image="busybox",
    )
