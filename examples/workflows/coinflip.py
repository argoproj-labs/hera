from hera.workflows import Container, Script, Steps, Workflow


def flip_coin_func() -> None:
    import random

    result = "heads" if random.randint(0, 1) == 0 else "tails"
    print(result)


with Workflow(
    generate_name="coinflip-",
    annotations={
        "workflows.argoproj.io/description": (
            "This is an example of coin flip defined as a sequence of conditional steps."
        ),
    },
) as w:
    heads = Container(
        name="heads",
        image="alpine:3.6",
        command=["sh", "-c"],
        args=["echo 'it was heads'"],
    )
    tails = Container(
        name="tails",
        image="alpine:3.6",
        command=["sh", "-c"],
        args=["echo 'it was tails'"],
    )

    flip_coin = Script(
        name="flip-coin",
        image="python:alpine3.6",
        command=["python"],
        source=flip_coin_func,
    )

    with Steps(name="coinflip") as s:
        fc = flip_coin()

        with s.parallel():
            heads(when=f"{fc.result} == heads")
            tails(when=f"{fc.result} == tails")
