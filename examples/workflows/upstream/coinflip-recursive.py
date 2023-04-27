from hera.workflows import Container, Step, Steps, Workflow, script


@script(image="python:alpine3.6", command=["python"], add_cwd_to_sys_path=False)
def flip_coin() -> None:
    import random

    result = "heads" if random.randint(0, 1) == 0 else "tails"
    print(result)


with Workflow(
    generate_name="coinflip-recursive-",
    entrypoint="coinflip",
) as w:
    heads = Container(
        name="heads",
        image="alpine:3.6",
        command=["sh", "-c"],
        args=['echo "it was heads"'],
    )

    with Steps(name="coinflip") as s:
        fc: Step = flip_coin()

        with s.parallel():
            heads(when=f"{fc.result} == heads")
            Step(name="tails", template=s, when=f"{fc.result} == tails")
