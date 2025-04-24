from hera.workflows import Workflow
from hera.workflows.models import Container, Template

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    annotations={"workflows.argoproj.io/description": "This is a simple hello world example."},
    generate_name="hello-world-",
    labels={"workflows.argoproj.io/archive-strategy": "false"},
    entrypoint="hello-world",
    templates=[
        Template(
            container=Container(
                args=["hello world"],
                command=["echo"],
                image="busybox",
            ),
            name="hello-world",
        )
    ],
) as w:
    pass
