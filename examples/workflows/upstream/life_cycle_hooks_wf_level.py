from hera.workflows import (
    HTTP,
    Container,
    Steps,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="lifecycle-hook-",
    entrypoint="main",
    hooks={
        "exit": m.LifecycleHook(template="http"),
        "running": m.LifecycleHook(expression='workflow.status == "Running"', template="http"),
    },
) as w:
    heads = Container(
        name="heads",
        image="alpine:3.6",
        command=["sh", "-c"],
        args=['echo "it was heads"'],
    )
    http = HTTP(
        name="http",
        url="https://raw.githubusercontent.com/argoproj/argo-workflows/4e450e250168e6b4d51a126b784e90b11a0162bc/pkg/apis/workflow/v1alpha1/generated.swagger.json",
    )
    with Steps(name="main"):
        heads(name="step1")
