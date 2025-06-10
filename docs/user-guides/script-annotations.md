# Script Annotations

You can use `typing.Annotated` to declare `Parameters` and `Artifacts` as metadata on the input and output types of a
`script` function. Hera automatically infers fields such as `name` and `path`, and annotations can simplify script
functions when using parameters and artifacts with additional fields such as a `description`.

## Inputs

### Parameters

You can usually just use standard non-`Annotated` Python function variables for input Parameters, but if you need the
extra fields, they can be declared as follows:

```python
@script()
def echo(
    an_int: Annotated[
        int,
        Parameter(description="an_int parameter", enum=[1, 2, 3]),
    ] = 1,
):
    print(an_int)
```

The fields allowed in the `Parameter` annotations are: `name`, `enum`, `description`, `loads` and `dumps`. All of them
are optional. A couple of things to note are:

* `name` is the name used in YAML and the Argo UI; it will default to the variable name if not provided.
* A `default` value must be set using standard Python syntax, i.e. `x: int = 42`.

> **Note:** `Annotated` can be used on both inline scripts and runner scripts!

<h4 id="parameters-custom-deserialisation">Custom Deserialisation</h4>

If you are using a type that is not a built in (`int`, `str`, `dict` etc) or a Pydantic `BaseModel`, you can provide
functions to the Parameter's `loads` (and `dumps`) attributes, which will be used by the Hera Runner (and so requires
the use of "runner" templates). These will then be used to deserialise from, and serialise to, strings. See the
[custom serialisation example](../examples/workflows/hera-runner/custom_serialiser.md).

#### Function parameter name aliasing

Script annotations can work on top of the `RunnerScriptConstructor` for name aliasing of function
parameters, in particular to allow a public `kebab-case` parameter, while using a `snake_case`
Python function parameter.

### Artifacts

> Note: `Artifact` annotations are only supported when used with the `RunnerScriptConstructor`.

Annotations are even more powerful for `Artifact`s. As seen in inline scripts, we must specify `Artifact`s in the
`inputs` of the decorator, but the path, or file itself, is not programmatically linked to the code within the function
through a variable:

```python
@script(inputs=Artifact(name="my-artifact", path="/tmp/file"))
def read_artifact():
     # Repeating "/tmp/file" is prone to human error!
    with open("/tmp/file") as a_file:
        print(a_file.read())
```

By using annotations, Hera can automatically infer the Artifact's name and create a path for us! The name will be the
function variable name, and the path will be `/tmp/hera-inputs/artifacts/var_name`. The function can then use the
variable directly as a `Path` object. The snippets below show how this helps to keep your code clean, the only
difference will be the name and path shown in the YAML:

=== "Hera Inferred"

    ```python
    @script(constructor="runner")
    def read_artifact(
        an_artifact: Annotated[Path, Artifact()]
    ):
        print(an_artifact.read_text())
    ```

=== "YAML Inferred"

    ```yaml
      - name: read-artifact
        inputs:
          artifacts:
          - name: an_artifact
            path: /tmp/hera-inputs/artifacts/an_artifact
        ...
    ```

=== "Hera Custom"

    ```python
    @script(constructor="runner")
    def read_artifact(
        an_artifact: Annotated[Path, Artifact(name="my-artifact-name", path="/tmp/an-artifact")]
    ):
        print(an_artifact.read_text())
    ```

=== "YAML Custom"

    ```yaml
      - name: read-artifact
        inputs:
          artifacts:
          - name: my-artifact-name
            path: /tmp/an-artifact
        ...
    ```

See [the `Artifact` class](../api/workflows/hera.md#hera.workflows.Artifact) for all the fields allowed in the
`Artifact` annotations. You are also able to use artifact repository types such as `S3Artifact` to first fetch the
artifact from storage and mount it to the container.

<h4 id="artifacts-custom-deserialisation">Custom Deserialisation</h4>

If you are using a type that is not a built in (`int`, `str`, `dict` etc) or a Pydantic `BaseModel`, you can provide
functions to the Artifact's `loads` and `dumps` attributes or the `loadb` and `dumpb` attributes, which will be used by
the Hera Runner (and so requires the use of "runner" templates).

* `loads` and `dumps` are used to deserialise from, and serialise to, strings.
* `loadb` and `dump` are used to deserialise from, and serialise to, a Python `bytes` object.

See the [custom serialisation example](../examples/workflows/hera-runner/custom_serialiser.md).

For simple use cases, you can set `loader` to an `ArtifactLoader` enum.

The `ArtifactLoader` enum lets you specify how the Hera Runner should load the Artifact into the Python variable. There
are three different ways that the Hera Runner can set the variable: as the Path to the Artifact, as the string contents
of the Artifact, or as the deserialized JSON object stored in the Artifact.

#### `None` loader

With `None` set as the loader (which is by default) in the Artifact annotation, the function parameter must be of `Path`
type. The `path` attribute of the `Artifact` is extracted and used to provide the `pathlib.Path` object for the given
argument, which can be used directly in the function body. The following example is the same as above except for
explicitly setting the loader to `None`, and letting Hera infer the name and path for us:

```python
@script(constructor="runner")
def read_artifact(an_artifact: Annotated[Path, Artifact(loader=None)]):
    print(an_artifact.read_text())
```

#### `file` loader

When the loader is set to `file`, the function parameter type must be of `str` type. The variable will then contain the
contents string representation of the file stored at `path` (essentially performing `path.read_text()` automatically):

```python
@script(constructor="runner")
def read_artifact(
    a_file_artifact: Annotated[str, Artifact(loader=ArtifactLoader.file)],
) -> str:
    return a_file_artifact
```

This loads the contents of the file to the argument `a_file_artifact` and subsequently can be used as a string inside the
function.

#### `json` loader

When the loader is set to `json`, the contents of the file at `path` are read and parsed to a dictionary via `json.load`
(essentially performing `json.load(path.open())` automatically).

```python
@script(constructor="runner")
def read_dict_artifact(
    dict_artifact: Annotated[dict, Artifact(loader=ArtifactLoader.json)],
) -> str:
    return dict_artifact["my-key"]
```

##### Pydantic Integration

A dictionary artifact would have no validation on its contents, so having safe code relies on you knowing or manually
validating the keys that exist in it. Instead, by specifying a Pydantic type, the input string can be automatically
deserialised and validated to that type, just as happens automatically for `Parameter` inputs:

```python
from pydantic import BaseModel

class MyArtifact(BaseModel):
    a = "hello "
    b = "world"


@script(constructor="runner")
def read_artifact(
    my_artifact: Annotated[MyArtifact, Artifact(loader=ArtifactLoader.json)],
) -> str:
    return my_artifact.a + my_artifact.b
```

Under the hood, this function receives an Artifact with a JSON representation of `MyArtifact`, such as
`{"a": "hello ", "b": "world"}`. We can tell Hera to `json.load` it by setting the `loader` to `ArtifactLoader.json`,
and as the type of `my_artifact` is a `BaseModel` subclass, Hera will try to create an object from the dictionary. Then
we can use `my_artifact` as normal Python inside the function, so the function will return `"hello world"`, which will
be printed to stdout.

## Outputs

> Note: Output annotations are currently only supported when used with the `RunnerScriptConstructor`.

Artifacts and Parameters behave very similarly for Outputs when using Annotations with Script Runner templates. There
are two ways to specify them as outputs.

### Function return annotations

Function return annotations specify the output type information for output Artifacts and Parameters, and the function
should return a single value or tuple. An example can be seen
[here](../examples/workflows/hera-runner/typed_script_input_output.md).

For a simple hello world output artifact example using an inline script we have:

```python
@script(outputs=Artifact(name="hello-artifact", path="/tmp/hello_world.txt"))
def hello_world():
   with open("/tmp/hello_world.txt", "w") as f:
       f.write("Hello, world!")
```

The `Annotated` approach allows us to return a value directly, and the Hera Runner will handle the serialisation and
writing to a file:

```python
@script()
def hello_world() -> Annotated[str, Artifact(name="hello-artifact")]:
    return "Hello, world!"
```

For `Parameter` we have a similar syntax:

```python
@script()
def hello_world() -> Annotated[str, Parameter(name="hello-param")]:
    return "Hello, world!"
```

You will see the returned values automatically saved in files within the Argo container according to this schema:

* `/tmp/hera-outputs/parameters/<name>`
* `/tmp/hera-outputs/artifacts/<name>`

These outputs are also exposed in the `outputs` section of the template in YAML.

The object returned from the function can be of any basic or Pydantic type and must be `Annotated` as an `Artifact` or
`Parameter`. The `Parameter`/`Artifact`'s `name` will be used for the path of the output. You generally won't need to
use a custom path, but can set one according to the following:

* if the annotation is an `Artifact` with a `path`, we use that `path`
* if the annotation is a `Parameter`, with a `value_from` that contains a `path`, we use that `path`

See the following two functions for specifying custom paths:

```python
@script()
def hello_world() -> Annotated[str, Artifact(name="hello-artifact", path="/tmp/hello_world_art.txt")]:
    return "Hello, world!"

@script()
def hello_world() -> Annotated[
    str, Parameter(name="hello-param", value_from={"path": "/tmp/hello_world_param.txt"})
]:
    return "Hello, world!"
```

For multiple outputs, the return type should be a `Tuple` of basic or Pydantic types with individual
`Parameter`/`Artifact` annotations, and the function must return a tuple from the function matching these types:

```python
@script()
def func(...) -> Tuple[
    Annotated[TypeA, Artifact(name="a", ...)],
    Annotated[TypeB, Parameter(name="b", ...)],
]:
    return output_a, output_b
```

You may prefer to use the [Script Runner IO](script-runner-io.md#script-outputs-using-output) classes instead to avoid
long return Tuples, as return values can be set by name, rather than position.

#### Custom Serialisation

As seen in the [Parameter Custom Deserialisation](#parameters-custom-deserialisation) and
[Artifact Custom Deserialisation](#artifacts-custom-deserialisation) sections, Parameters and Artifacts can be any type,
as long as you provide a serialisation function. For `Parameter` this is `dumps`, for `Artifact` this is `dumps` or
`dumpb`. See the [custom serialisation example](../examples/workflows/hera-runner/custom_serialiser.md) for more
details.

### Input-Output function parameters

To allow users to arbitrarily write to disk (e.g. streaming to an output), Hera allows `Parameter`/`Artifact` outputs to
be declared as a function input. They must be specified as a `Path` type, and the user will write to the path instead of
returning a value. They require an additional field `output=True` to distinguish them from the input parameters. You can
use Input-Outputs alongside standard function-return outputs.

```python
@script()
def func(
    output_param: Annotated[Path, Parameter(output=True, name="my-output")]
) -> Annotated[int, Parameter(name="my-other-output", ...)]:
    output_param.write_bytes(...)

    return 42
```

### Default Output Directory

The outputs directory, `/tmp/hera-outputs` by default, can be set by the user. This is done through the `global_config`:

```python
global_config.set_class_defaults(RunnerScriptConstructor, outputs_directory="user/chosen/outputs")
```
