# Script Runner IO

Hera provides the `Input` and `Output` Pydantic classes to help combat sprawling function declarations of inputs and
outputs when using script annotations for runner scripts. It has the added bonus of letting you return values by
referencing their name, instead of setting outputs by position in a `Tuple`.

It lets you go from a multiple-argument function declaration and a tuple `return` to a single input and output. Compare
the equivalent workflows below:

=== "Standard IO"

    ```py
    @script(constructor="runner")
    def my_function(
        param_int: int = 42,
        an_object: Annotated[MyObject, Parameter(name="obj-input")] = MyObject(
            a_dict={"my-key": "a-value"}, a_str="hello world!"
        ),
        artifact_int: Annotated[int, Artifact(name="artifact-input", loader=ArtifactLoader.json)],
    ) -> Tuple[
        Annotated[int, Parameter(name="param-int-output")],
        Annotated[int, Parameter(name="another-param-int-output")],
        Annotated[str, Parameter(name="a-str-param-output")],
    ]:
        print(param_int)
        print(artifact_int)
        ...
        return 42, -1, "Hello, world!"  # Hope I didn't mix these up!
    ```

=== "Script Runner IO"

    ```py
    from hera.workflows.io import Input, Output

    class MyInput(Input):
        param_int: int = 42
        an_object: Annotated[MyObject, Parameter(name="obj-input")] = MyObject(
            a_dict={"my-key": "a-value"}, a_str="hello world!"
        )
        artifact_int: Annotated[int, Artifact(name="artifact-input", loader=ArtifactLoader.json)]

    class MyOutput(Output):
        param_int_output: Annotated[int, Parameter(name="param-int-output")],
        another_param_int_output: Annotated[int, Parameter(name="another-param-int-output")],
        a_str_param_output: Annotated[str, Parameter(name="a-str-param-output")],

    @script(constructor="runner")
    def my_function(my_input: MyInput) -> MyOutput:
        print(my_input.param_int)
        print(my_input.artifact_int)
        ...
        return MyOutput(
            param_int_output=42,
            another_param_int_output=-1,
            a_str_param_output="Hello, world!",
        )
    ```

## Pydantic V1 or V2?

Importing `Input` and `Output` from the `hera.workflows.io` submodule automatically matches the version of your Pydantic
installation.

If you need to use V1 models when you have V2 installed, you should import `Input` and `Output` from the
`hera.workflows.io.v1` (or `hera.workflows.io.v2`) module explicitly. The V2 models **will not be available** if you
have installed `pydantic<2`, but the V1 models are usable for either version, allowing you to migrate at your own pace.

## Script Inputs Using `Input`

For script inputs, you should create a subclass class of `Input`, and declare all your input parameters (and artifacts)
as fields of the class. You can use `Annotated` to declare `Artifacts` add metadata to your `Parameters`.

```py
from typing import Annotated
from pydantic import BaseModel

from hera.workflows import Artifact, ArtifactLoader, Parameter, script
from hera.workflows.io import Input


class MyObject(BaseModel):
    """This is a model class, to be used within an Input."""
    a_dict: dict
    a_str: str = "a default string"


class MyInput(Input):
    """This is the Input class."""
    param_int: int = 42
    an_object: Annotated[MyObject, Parameter(name="obj-input")] = MyObject(
        a_dict={"my-key": "a-value"}, a_str="hello world!"
    )
    artifact_int: Annotated[int, Artifact(name="artifact-input", loader=ArtifactLoader.json)]


@script(constructor="runner")
def pydantic_io(
    my_input: MyInput,
) -> ...:
    ...
```

This will create a script template named `pydantic_io`, with input parameters `"param_int"` and `"obj-input"`, but _not_
`"my_input"`; the template will also have the `"artifact-input"` artifact. The YAML generated from the Python will look
like the following:

```yaml
  templates:
  - name: pydantic-io
    inputs:
      parameters:
      - name: param-input
        default: '42'
      - name: obj-input
        default: '{"a_dict": {"my-key": "a-value"}, "a_str": "hello world!"}'
      artifacts:
      - name: artifact-input
        path: /tmp/hera-inputs/artifacts/artifact-input
    script:
      ...
```

## Script Outputs Using `Output`

The `Output` class works in the same way as `Input`, but comes with two extra special variables, `exit_code` and
`result`. The `exit_code` is used to exit the container when running on Argo with the specific exit code - it is set to
`0` by default. The `result` is used to print any serializable object to stdout, allowing you to use the `result` output
parameter between steps or tasks.

> If you want an output parameters/artifacts with the name `exit_code` or `result`, you can declare another field with
> an annotation of that name, e.g. `my_exit_code: Annotated[int, Parameter(name="exit_code")]`.

Aside from the `exit_code` and `result`, the `Output` behaves exactly like the `Input`:

```py
from typing import Annotated

from hera.workflows import Artifact, Parameter, script
from hera.workflows.io import Output


class MyOutput(Output):
    param_int: Annotated[int, Parameter(name="param-output")]
    artifact_int: Annotated[int, Artifact(name="artifact-output")]


@script(constructor="runner")
def pydantic_io() -> MyOutput:
    return MyOutput(exit_code=1, result="Test!", param_int=42, artifact_int=my_input.param_int)
```

See the full Pydantic IO example [here](../examples/workflows/scripts/script_runner_io.md)!
