from hera.workflows import Container, Workflow
from hera.workflows.models import Mutex, Synchronization

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="synchronization-wf-level-",
    entrypoint="hello-world",
    synchronization=Synchronization(
        mutex=Mutex(
            name="test",
        ),
    ),
) as w:
    Container(
        name="hello-world",
        args=["hello world"],
        command=["echo"],
        image="busybox",
    )
