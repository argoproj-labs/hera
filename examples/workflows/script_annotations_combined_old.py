from hera.workflows import Workflow, script
from hera.workflows.parameter import Parameter
from hera.workflows.steps import Steps


@script(
    inputs=[
        Parameter(name="an_int", description="an_int parameter", default=1, enum=[1, 2, 3]),
        Parameter(name="a_bool", description="a_bool parameter", default=True, enum=[True, False]),
        Parameter(name="a_string", description="a_string parameter", default="a", enum=["a", "b", "c"]),
    ]
)
def echo_all(an_int, a_bool, a_string):
    print(an_int)
    print(a_bool)
    print(a_string)


with Workflow(generate_name="test-types-", entrypoint="my_steps") as w:
    with Steps(name="my_steps") as s:
        echo_all(arguments={"an_int": 1, "a_bool": True, "a_string": "a"})
