from hera.workflows.v5.container import Container
from hera.workflows.v5.workflow import Workflow


def test_workflow_v5():
    # GIVEN
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
    # WHEN
    output = w.build().to_dict()
    # THEN
    assert output == {
        "apiVersion": "argoproj.io/v1alpha1",
        "metadata": {
            "annotations": {
                "workflows.argoproj.io/description": "This is an "
                "example of "
                "coin flip "
                "defined as "
                "a sequence "
                "of "
                "conditional "
                "steps."
            },
            "generateName": "coinflip-",
            "namespace": "default",
        },
        "spec": {
            "templates": [
                {
                    "container": {"args": ["echo 'it was heads'"], "command": ["sh", "-c"], "image": "alpine:3.6"},
                    "name": "heads",
                },
                {
                    "container": {"args": ["echo 'it was tails'"], "command": ["sh", "-c"], "image": "alpine:3.6"},
                    "name": "tails",
                },
            ]
        },
    }
