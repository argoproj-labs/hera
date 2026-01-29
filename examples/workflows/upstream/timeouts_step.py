from hera.workflows import Container, Workflow

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="timeouts-step-",
    entrypoint="sleep",
) as w:
    Container(
        active_deadline_seconds=10,
        name="sleep",
        args=["echo 123; sleep 1d"],
        command=["bash", "-c"],
        image="argoproj/argosay:v2",
    )
