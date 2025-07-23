from hera.workflows import Container, Workflow
from hera.workflows.models import Arguments, Parameter

with Workflow(
    arguments=Arguments(
        parameters=[
            Parameter(
                name="mem-limit",
                value="100Mi",
            )
        ],
    ),
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="pod-spec-patch-",
    entrypoint="hello-world",
    pod_spec_patch='containers:\n  - name: main\n    resources:\n      limits:\n        memory: "{{workflow.parameters.mem-limit}}"\n',
) as w:
    Container(
        name="hello-world",
        args=["hello world"],
        command=["echo"],
        image="busybox",
    )
