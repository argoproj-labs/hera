from hera.workflows import Container, Resource, Step, Steps, Workflow

with Workflow(
    generate_name="workflow-of-workflows-1-",
    entrypoint="echo",
) as w1:
    Container(name="s", image="docker/whalesay:latest")

with Workflow(
    generate_name="workflow-of-workflows-2-",
    entrypoint="echo",
) as w2:
    Container(name="s", image="docker/whalesay:latest")

with Workflow(generate_name="workflow-of-workflows-", entrypoint="main") as w:
    w1_res = Resource(
        name="w1-res",
        action="create",
        manifest=w1,
        success_condition="status.phase == Succeeded",
        failure_condition="status.phase in (Failed, Error)",
    )

    w2_res = Resource(
        name="w2-res",
        action="create",
        manifest=w2,
        success_condition="status.phase == Succeeded",
        failure_condition="status.phase in (Failed, Error)",
    )

    with Steps(name="main"):
        Step(name="workflow1", template=w1_res)
        Step(name="workflow2", template=w2_res)
