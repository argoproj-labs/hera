from hera.workflows import Workflow, script
from hera.workflows.parameter import Parameter
from hera.workflows.steps import Steps


@script(inputs=[Parameter(name="an_int", enum=[1, 2, 3])])
def echo_int(an_int):
    print(an_int)


@script(inputs=[Parameter(name="a_bool", enum=[True])])
def echo_boolean(a_bool):
    print(a_bool)


@script(inputs=[Parameter(name="a_string", enum=["a", "b", "c"])])
def echo_string(a_string):
    print(a_string)


with Workflow(generate_name="test-types-", entrypoint="my_steps") as w:
    with Steps(name="my_steps") as s:
        echo_int(arguments={"an_int": 1})
        echo_boolean(arguments={"a_bool": True})
        echo_string(arguments={"a_string": "a"})
