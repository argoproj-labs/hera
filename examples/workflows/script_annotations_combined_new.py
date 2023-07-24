try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

from hera.shared import global_config
from hera.workflows import Workflow, script
from hera.workflows.parameter import Parameter
from hera.workflows.steps import Steps

global_config.experimental_features["script_annotations"] = True


@script()
def echo_all(
    an_int: Annotated[int, Parameter(description="an_int parameter", default=1, enum=[1, 2, 3])],
    a_bool: Annotated[bool, Parameter(description="a_bool parameter", default=True, enum=[True, False])],
    a_string: Annotated[str, Parameter(description="a_string parameter", default="a", enum=["a", "b", "c"])],
):
    print(an_int)
    print(a_bool)
    print(a_string)


with Workflow(generate_name="test-types-", entrypoint="my_steps") as w:
    with Steps(name="my_steps") as s:
        echo_all(arguments={"an_int": 1, "a_bool": True, "a_string": "a"})
