from hera.workflows import (
    HTTP,
    Container,
    Steps,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="lifecycle-hook-tmpl-level-",
    entrypoint="main",
) as w:
    echo = Container(
        name="echo",
        image="alpine:3.6",
        command=["sh", "-c"],
        args=['echo "it was heads"'],
    )
    http = HTTP(
        name="http",
        url="https://raw.githubusercontent.com/argoproj/argo-workflows/4e450e250168e6b4d51a126b784e90b11a0162bc/pkg/apis/workflow/v1alpha1/generated.swagger.json",
    )
    with Steps(name="main"):
        echo(
            name="step-1",
            hooks={
                "running": m.LifecycleHook(expression='steps["step-1"].status == "Running"', template="http"),
                "success": m.LifecycleHook(expression='steps["step-1"].status == "Succeeded"', template="http"),
            },
        )
        echo(
            name="step2",
            hooks={
                "running": m.LifecycleHook(expression='steps.step2.status == "Running"', template="http"),
                "success": m.LifecycleHook(expression='steps.step2.status == "Succeeded"', template="http"),
            },
        )
