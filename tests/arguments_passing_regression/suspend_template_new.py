from hera.workflows import Container, Steps, Suspend, Workflow

with Workflow(
    generate_name="suspend-template-",
    entrypoint="suspend",
) as w:
    whalesay = Container(
        name="whalesay", image="docker/whalesay", command=["cowsay"], args=["hello world"], directly_callable=True
    )

    approve = Suspend(name="approve")
    delay = Suspend(name="delay", duration=20)

    with Steps(name="suspend"):
        whalesay().with_(name="build")
        approve()
        delay()
        whalesay().with_(name="release")
