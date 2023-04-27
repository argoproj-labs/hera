from hera.workflows import Container, Steps, Suspend, Workflow

with Workflow(
    generate_name="suspend-template-",
    entrypoint="suspend",
) as w:
    whalesay = Container(name="whalesay", image="docker/whalesay", command=["cowsay"], args=["hello world"])

    approve = Suspend(name="approve")
    delay = Suspend(name="delay", duration=20)

    with Steps(name="suspend"):
        whalesay(name="build")
        approve()
        delay()
        whalesay(name="release")
