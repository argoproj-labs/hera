from hera.workflows import Container, Workflow

with Workflow(
    name="forever",
    entrypoint="main",
) as w:
    Container(
        name="main",
        image="busybox",
        command=["sh", "-c", "for I in $(seq 1 1000) ; do echo $I ; sleep 1s; done"],
    )
