from hera.workflows import Container, Workflow
from hera.workflows.models import Arguments, Parameter

with Workflow(
    arguments=Arguments(
        parameters=[
            Parameter(
                name="cpu-limit",
                value="100m",
            )
        ],
    ),
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="pod-spec-patch-",
    entrypoint="hello-world",
) as w:
    Container(
        name="hello-world",
        pod_spec_patch='{"containers":[{"name":"main", "resources":{"limits":{"cpu": "{{workflow.parameters.cpu-limit}}" }}}]}',
        args=["hello world"],
        command=["echo"],
        image="busybox",
    )
