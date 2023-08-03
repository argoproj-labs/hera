from hera.workflows import Workflow, script
from hera.workflows.steps import Steps


@script()
def echo_int(an_int=1):
    print(an_int)


@script()
def echo_boolean(a_bool=True):
    print(a_bool)


@script()
def echo_string(a_string="a"):
    print(a_string)


with Workflow(generate_name="test-types-", entrypoint="my_steps") as w:
    with Steps(name="my_steps") as s:
        echo_int(arguments={"an_int": 1})
        echo_boolean(arguments={"a_bool": True})
        echo_string(arguments={"a_string": "a"})
