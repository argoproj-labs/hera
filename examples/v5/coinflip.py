from hera.workflows.v5.workflow import Workflow
from hera.workflows.v5.container import Container

with Workflow(generate_name="coinflip-", annotations={
    "workflows.argoproj.io/description": "This is an example of coin flip defined as a sequence of conditional steps."
}) as w:
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

w.create()
