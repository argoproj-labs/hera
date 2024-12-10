# Script Runner IO

Hera provides the `Input` and `Output` Pydantic classes to help combat sprawling function declarations of inputs and
outputs when using script annotations. It has the added bonus of letting you return values by referencing their name,
instead of setting outputs by position in a `Tuple`.

It lets you go from a function declaration and `return` like this:

```py
@script(constructor="runner")
def my_function(
    param_int: Annotated[int, Parameter(name="param-input")] = 42,
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
    ...
    return 42, -1, "Hello, world!"  # Hope I didn't mix these up!
```

to a function that uses the `Input` and `Output` classes:

```py
from hera.workflows.io import Input, Output

class MyInput(Input):
    param_int: Annotated[int, Parameter(name="param-input")] = 42
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
    ...
    return MyOutput(
        param_int_output=42,
        another_param_int_output=-1,
        a_str_param_output="Hello, world!",
    )
```

Using the IO classes requires use of the Hera Runner and the `"script_pydantic_io"` experimental feature flag to be
enabled:

```py
global_config.experimental_features["script_pydantic_io"] = True
```

## Pydantic V1 or V2?

You can import `Input` and `Output` from the `hera.workflows.io` submodule to import the version of Pydantic
that matches your V1 or V2 installation.

If you need to use V1 models when you have V2 installed, you should import
`Input` and `Output` from the `hera.workflows.io.v1` or `hera.workflows.io.v2` module explicitly. The V2
models will not be available if you have installed `pydantic<2`, but the V1 models are usable for either version,
allowing you to migrate at your own pace.

## Script inputs using `Input`

For your script inputs, you can create a derived class of `Input`, and declare all your input parameters (and
artifacts) as fields of the class. You can use `Annotated` to declare `Artifacts` add metadata to your
`Parameters`.

```py
from typing import Annotated
from pydantic import BaseModel

from hera.workflows import Artifact, ArtifactLoader, Parameter, script
from hera.workflows.io import Input


class MyObject(BaseModel):
    a_dict: dict
    a_str: str = "a default string"


class MyInput(Input):
    param_int: Annotated[int, Parameter(name="param-input")] = 42
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

This will create a script template named `pydantic_io`, with input parameters `"param-input"` and `"obj-input"`, but
_not_ `"my_input"` (hence inline script templates will not work, as references to `my_input` will not resolve); the
template will also have the `"artifact-input"` artifact. The yaml generated from the Python will look something like the following:

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

## Script outputs using `Output`

The `Output` class comes with two special variables, `exit_code` and `result`. The `exit_code` is used to exit the
container when running on Argo with the specific exit code - it is set to `0` by default. The `result` is used to print
any serializable object to stdout, which means you can now use `.result` on tasks or steps that use a "runner
constructor" script - you should be mindful of printing/logging anything else to stdout, which will stop the `result`
functionality working as intended. If you want an output parameters/artifacts with the name `exit_code` or `result`, you
can declare another field with an annotation of that name, e.g.
`my_exit_code: Annotated[int, Parameter(name="exit_code")]`.

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

See the full Pydantic IO example [here](../examples/workflows/experimental/script_runner_io.md)!
