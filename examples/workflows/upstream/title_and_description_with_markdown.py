from hera.workflows import Container, Workflow

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    annotations={
        "workflows.argoproj.io/title": "**Test Title**",
        "workflows.argoproj.io/description": "`This is a simple hello world example.`\nThis is an embedded link to the docs: https://argo-workflows.readthedocs.io/en/latest/title-and-description/\n",
    },
    generate_name="title-and-description-with-markdown-",
    labels={"workflows.argoproj.io/archive-strategy": "false"},
    entrypoint="hello-world",
) as w:
    Container(
        name="hello-world",
        args=["hello world"],
        command=["echo"],
        image="busybox",
    )
