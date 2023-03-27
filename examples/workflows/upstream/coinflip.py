from hera.workflows import Container, Steps, Workflow, script


@script(image="python:alpine3.6", command=["python"], add_cwd_to_sys_path=False)
def flip_coin() -> None:
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
    entrypoint="coinflip",
) as w:
    heads = Container(
        name="heads",
        image="alpine:3.6",
        command=["sh", "-c"],
        args=['echo "it was heads"'],
    )
    tails = Container(
        name="tails",
        image="alpine:3.6",
        command=["sh", "-c"],
        args=['echo "it was tails"'],
    )

    with Steps(name="coinflip") as s:
        fc = flip_coin(name="flip-coin")

        with s.parallel():
            heads(when=f"{fc.result} == heads")
            tails(when=f"{fc.result} == tails")
