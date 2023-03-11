from hera.workflows.container import Container
from hera.workflows.workflow import Workflow

with Workflow(
    generate_name="coinflip-",
    annotations={
        "workflows.argoproj.io/description": (
            "This is an example of coin flip defined as a sequence of conditional steps."
        ),
    },
) as w:
    Container(
        name="heads",
        image="alpine:3.6",
        command=["sh", "-c"],
        args=["echo 'it was heads'"],
    )
    Container(
        name="tails",
        image="alpine:3.6",
        command=["sh", "-c"],
        args=["echo 'it was tails'"],
    )
