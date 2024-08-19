from hera.workflows import Container, Steps, Suspend, Workflow

with Workflow(
    generate_name="suspend-template-",
    entrypoint="suspend",
) as w:
    hello_world = Container(name="hello-world", image="busybox", command=["echo"], args=["hello world"])

    approve = Suspend(name="approve")
    delay = Suspend(name="delay", duration=20)

    with Steps(name="suspend"):
        hello_world(name="build")
        approve()
        delay()
        hello_world(name="release")
