from hera.workflows import Container, Script, Step, Steps, Workflow

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="coinflip-",
    entrypoint="coinflip",
) as w:
    with Steps(
        name="coinflip",
    ) as invocator:
        Step(
            name="flip-coin",
            template="flip-coin",
        )
        with invocator.parallel():
            Step(
                name="heads",
                template="heads",
                when="{{steps.flip-coin.outputs.result}} == heads",
            )
            Step(
                name="tails",
                template="tails",
                when="{{steps.flip-coin.outputs.result}} == tails",
            )
        Step(
            name="flip-again",
            template="flip-coin",
        )
        with invocator.parallel():
            Step(
                name="complex-condition",
                template="heads-tails-or-twice-tails",
                when="( {{steps.flip-coin.outputs.result}} == heads &&\n  {{steps.flip-again.outputs.result}} == tails\n) || ( {{steps.flip-coin.outputs.result}} == tails &&\n  {{steps.flip-again.outputs.result}} == tails )",
            )
            Step(
                name="heads-regex",
                template="heads",
                when="{{steps.flip-again.outputs.result}} =~ hea",
            )
            Step(
                name="tails-regex",
                template="tails",
                when="{{steps.flip-again.outputs.result}} =~ tai",
            )
    Script(
        name="flip-coin",
        command=["python"],
        image="python:alpine3.6",
        source='import random\nresult = "heads" if random.randint(0,1) == 0 else "tails"\nprint(result)\n',
    )
    Container(
        name="heads",
        args=['echo "it was heads"'],
        command=["sh", "-c"],
        image="alpine:3.6",
    )
    Container(
        name="tails",
        args=['echo "it was tails"'],
        command=["sh", "-c"],
        image="alpine:3.6",
    )
    Container(
        name="heads-tails-or-twice-tails",
        args=['echo "it was heads the first flip and tails the second. Or it was two times tails."'],
        command=["sh", "-c"],
        image="alpine:3.6",
    )
