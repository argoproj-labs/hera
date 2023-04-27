from hera.workflows import Container, Step, Steps, Suspend, Workflow

with Workflow(
    generate_name="suspend-template-",
    entrypoint="suspend",
) as w:
    whalesay = Container(name="whalesay", image="docker/whalesay", command=["cowsay"], args=["hello world"])

    approve = Suspend(name="approve")
    delay = Suspend(name="delay", duration=20)

    with Steps(name="suspend"):
        whalesay(name="build")
        Step(name="approve", template=approve)
        Step(name="delay", template=delay)
        whalesay(name="release")
