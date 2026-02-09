"""This example shows the various forms of IO available to Script Template functions.

Pydantic classes, as well as JSON types (and any combination of them), are usable as inputs and
outputs in script template functions, as the Hera Runner understands Pydantic classes, so can
serialise and deserialise them.

If you need the Pydantic V1 BaseModel when V2 is installed, use this import block:

```py
try:
    from pydantic.v1 import BaseModel
except (ImportError, ModuleNotFoundError):
    from pydantic import BaseModel
```
"""

from typing import Annotated, List, Union

from pydantic import BaseModel

from hera.shared import global_config
from hera.shared.serialization import serialize
from hera.workflows import Parameter, Script, Steps, Workflow, script

# Note, you must build an image to use the Hera Runner
global_config.image = "my-image-with-python-source-code-and-dependencies"
global_config.set_class_defaults(Script, constructor="runner")


# Create a BaseModel sub-class to use a JSON input with any shape.
# It will be validated by Pydantic at runtime.
class MyInput(BaseModel):
    a: int
    b: str = "foo"
    c: Union[str, int, float]


# Create a BaseModel sub-class to use a JSON output with any shape.
# It will be validated by Pydantic at runtime.
class MyOutput(BaseModel):
    output: List[MyInput]


@script()
def my_function(input: MyInput) -> MyOutput:
    return MyOutput(output=[input])


# You can use lists (or dictionaries) of your custom type as input
@script()
def another_function(inputs: List[MyInput]) -> MyOutput:
    return MyOutput(output=inputs)


# Raw json strings must be explicitly marked as a string type to ensure
# the Hera Runner does not parse it for you.
@script()
def str_function(input: str) -> MyOutput:
    # Example function to ensure string type is not auto-parsed by Hera
    return MyOutput(output=[MyInput.model_validate_json(input)])


# Use Script Annotations to seamlessly alias names for your template interface,
# in particular, you can use "snake_case" code with a "kebab-case" interface:
@script()
def function_kebab(
    a_snake: Annotated[int, Parameter(name="a-but-kebab")] = 2,
    b_snake: Annotated[str, Parameter(name="b-but-kebab")] = "foo",
    c_snake: Annotated[float, Parameter(name="c-but-kebab")] = 42.0,
) -> MyOutput:
    return MyOutput(output=[MyInput(a=a_snake, b=b_snake, c=c_snake)])


@script()
def function_kebab_object(annotated_input_value: Annotated[MyInput, Parameter(name="input-value")]) -> MyOutput:
    return MyOutput(output=[annotated_input_value])


with Workflow(name="my-workflow", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        my_function(arguments={"input": MyInput(a=2, b="bar", c=42)})
        str_function(arguments={"input": serialize(MyInput(a=2, b="bar", c=42))})
        another_function(arguments={"inputs": [MyInput(a=2, b="bar", c=42), MyInput(a=2, b="bar", c=42.0)]})
        function_kebab(arguments={"a-but-kebab": 3, "b-but-kebab": "bar"})
        function_kebab_object(arguments={"input-value": MyInput(a=3, b="bar", c="42")})
