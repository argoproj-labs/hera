from hera.workflows import Container, Workflow
from hera.workflows.models import TTLStrategy

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="gc-ttl-",
    entrypoint="hello-world",
    ttl_strategy=TTLStrategy(
        seconds_after_completion=10,
        seconds_after_failure=5,
        seconds_after_success=5,
    ),
) as w:
    Container(
        name="hello-world",
        args=["hello world"],
        command=["echo"],
        image="busybox",
    )
