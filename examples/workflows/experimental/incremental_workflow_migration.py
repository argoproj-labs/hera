from hera.shared import global_config
from hera.workflows import Input, Output, Steps, Workflow, script

global_config.experimental_features["context_manager_pydantic_io"] = True


class MyInput(Input):
    value: int


class MyOutput(Output):
    value: int


# Function migrated to Pydantic I/O
@script()
def double(input: MyInput) -> MyOutput:
    return MyOutput(value=input.value * 2)


# Not yet migrated to Pydantic I/O
@script()
def print_value(value: int) -> None:
    print("Value was", value)


# Not yet migrated to decorator syntax
with Workflow(name="my-template") as w:
    with Steps(name="steps"):
        # Can now pass Pydantic types to/from functions
        first_step = double(Input(value=5))
        # Results can be passed into non-migrated functions
        print_value(arguments={"value": first_step.value})
