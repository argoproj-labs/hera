from hera.workflows import Container, Resources, Workflow

with Workflow(
    generate_name="pod-resources-",
    entrypoint="hello-world",
    pod_resources=Resources(
        cpu_request="100m",
        memory_request="64Mi",
        cpu_limit="1",
        memory_limit="512Mi",
    ),
) as w:
    Container(
        name="hello-world",
        image="busybox",
        command=["echo"],
        args=["hello world"],
    )
