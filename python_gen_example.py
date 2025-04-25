from hera.workflows import Container, Workflow

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    annotations={"workflows.argoproj.io/description": "This is a simple hello world example."},
    generate_name="hello-world-",
    labels={"workflows.argoproj.io/archive-strategy": "false"},
    entrypoint="hello-world",
) as w:
    Container(
        name="hello-world",
        image="busybox",
        command=["echo"],
        args=["hello world"],
    )
