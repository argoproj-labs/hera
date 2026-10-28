from hera.workflows import Container, Resources, Step, Steps, UserContainer, Workflow

with Workflow(
    generate_name="pod-resources-template-override-",
    entrypoint="main",
    pod_resources=Resources(cpu_limit="1", memory_limit="512Mi"),
) as w:
    small = Container(
        name="small",
        image="busybox",
        command=["echo"],
        args=["small step"],
    )
    large = Container(
        name="large",
        pod_resources=Resources(cpu_limit="2", memory_limit="1Gi"),
        image="busybox",
        command=["sh", "-c"],
        args=["sleep 5; echo large step"],
        sidecars=UserContainer(name="helper", image="busybox", command=["sh", "-c"], args=["sleep 10"]),
    )

    with Steps(name="main") as s:
        Step(name="small", template=small)
        Step(name="large", template=large)
