from hera.workflows import Container, Resource, Step, Steps, Workflow

with Workflow(
    generate_name="sub-workflow-1-",
    entrypoint="echo",
) as sub_workflow_1:
    Container(
        name="echo",
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=["I'm workflow 1"],
    )

with Workflow(
    generate_name="sub-workflow-2-",
    entrypoint="echo",
) as sub_workflow_2:
    Container(
        name="echo",
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=["I'm workflow 2"],
    )

with Workflow(generate_name="workflow-of-workflows-", entrypoint="main") as w:
    w1_resource = Resource(
        name="w1-resource",
        action="create",
        manifest=sub_workflow_1,
        success_condition="status.phase == Succeeded",
        failure_condition="status.phase in (Failed, Error)",
    )

    w2_resource = Resource(
        name="w2-resource",
        action="create",
        manifest=sub_workflow_2,
        success_condition="status.phase == Succeeded",
        failure_condition="status.phase in (Failed, Error)",
    )

    with Steps(name="main"):
        Step(name="sub-workflow-1", template=w1_resource)
        Step(name="sub-workflow-2", template=w2_resource)
