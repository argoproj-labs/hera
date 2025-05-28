import pickle
from typing import Annotated, Tuple

from hera.workflows import (
    DAG,
    Artifact,
    NoneArchiveStrategy,
    Parameter,
    Task,
    Workflow,
    script,
)


class CustomClass:
    """Represents a non-user-defined class (e.g. pandas DataFrame) that does not inherit from BaseModel."""

    def __init__(self, a: str, b: str):
        self.a = a
        self.b = b

    @classmethod
    def from_custom(cls, custom: str) -> "CustomClass":
        split = custom.split()
        return cls(a=split[0], b=" custom " + split[1])


@script(constructor="runner", image="my-image:v1")
def create_outputs() -> Tuple[
    Annotated[
        str,
        Artifact(
            name="binary-output",
            dumpb=pickle.dumps,
            archive=NoneArchiveStrategy(),
        ),
    ],
    Annotated[str, Parameter(name="param-output", dumps=lambda x: x + "!")],
]:
    return "some bytes", "hello world"


@script(constructor="runner", image="my-image:v1")
def consume_outputs(
    a_parameter: Annotated[
        CustomClass,
        Parameter(name="my-parameter", loads=CustomClass.from_custom),
    ],
    an_artifact: Annotated[
        bytes,
        Artifact(
            name="binary-artifact",
            loadb=lambda b: pickle.loads(b),
        ),
    ],
) -> str:
    print(an_artifact)
    return a_parameter.a + a_parameter.b


with Workflow(generate_name="param-passing-", entrypoint="d", service_account_name="argo") as w:
    with DAG(name="d"):
        create_task: Task = create_outputs()
        consume_task = consume_outputs(
            arguments={
                "my-parameter": create_task.get_parameter("param-output"),
                "binary-artifact": create_task.get_artifact("binary-output"),
            },
        )

        create_task >> consume_task
