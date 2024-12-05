# Script Annotations

Annotation syntax uses `typing.Annotated` to declare `Parameters` and `Artifacts` as metadata on the input and output
types of a `script` function. This simplifies script functions with parameters and artifacts that require additional
fields such as a `description`, and allows Hera to automatically infer fields such as `name` and `path`.

## Parameters

In Hera, we can specify inputs inside the `@script` decorator as follows:

```python
@script(
    inputs=[
        Parameter(name="an_int", description="an_int parameter", default=1, enum=[1, 2, 3]),
        Parameter(name="a_bool", description="a_bool parameter", default=True, enum=[True, False]),
        Parameter(name="a_string", description="a_string parameter", default="a", enum=["a", "b", "c"])
    ]
)
def echo_all(an_int=1, a_bool=True, a_string="a"):
    print(an_int)
    print(a_bool)
    print(a_string)
```

Notice how the `name` and `default` values are duplicated for each `Parameter` as Python function parameters. Using
annotations, we can rewrite this as:

```python
@script()
def echo_all(
    an_int: Annotated[int, Parameter(description="an_int parameter", enum=[1, 2, 3])] = 1,
    a_bool: Annotated[bool, Parameter(description="a_bool parameter", enum=[True, False])] = True,
    a_string: Annotated[str, Parameter(description="a_string parameter", enum=["a", "b", "c"])] = "a",
):
    print(an_int)
    print(a_bool)
    print(a_string)
```

The fields allowed in the `Parameter` annotations are: `name`, `enum`, and `description`, `name` will be set to the
variable name if not provided (when exporting to YAML or viewing in the Argo UI, the `name` variable will be used). A
`default` must be set using standard Python syntax, i.e. `x: int = 42`.

## Artifacts

> Note: `Artifact` annotations are only supported when used with the `RunnerScriptConstructor`.

The feature is even more powerful for `Artifact`s. In Hera we are able to specify `Artifact`s in `inputs`, but the given
path is not programmatically linked to the code within the function unless defined outside the scope of the function:

```python
@script(inputs=Artifact(name="my-artifact", path="/tmp/file"))
def read_artifact():
    with open("/tmp/file") as a_file:  # Repeating "/tmp/file" is prone to human error!
        print(a_file.read())

# or

MY_PATH = "/tmp/file"  # Now accessible outside of the function scope!
@script(inputs=Artifact(name="my-artifact", path=MY_PATH))
def read_artifact():
    with open(MY_PATH) as a_file:
        print(a_file.read())
```

By using annotations we can avoid repeating the `path` of the file, and even let let Hera automatically infer the
Artifact's name and create a path for us! (We can still set a custom name and path if we want.) The function can then
use the variable directly as a `Path` object:

```python
@script(constructor="runner")
def read_artifact(an_artifact: Annotated[Path, Artifact(name="my-artifact-name", path="/tmp/my-custom-file-path")]):
    print(an_artifact.read_text())
```

The fields allowed in the `Artifact` annotations are: `name`, `path`, and `loader`. You are also able to use artifact
repository types such as `S3Artifact` (which are subclasses of `Artifact`) to first fetch the artifact from storage and
mount it to the container at the inferred path (or your custom path).

## Artifact Loaders

Artifact loaders specify how the Hera Runner should load the Artifact into the Python variable. There are three
different ways that the Hera Runner can set the variable: as the Path to the Artifact, as the string contents of the
Artifact, or as the deserialized JSON object stored in the Artifact.

### `None` loader

With `None` set as the loader (which is by default) in the Artifact annotation, the function parameter must be of `Path`
type. The `path` attribute of the `Artifact` is extracted and used to provide the `pathlib.Path` object for the given
argument, which can be used directly in the function body. The following example is the same as above except for
explicitly setting the loader to `None`, and letting Hera infer the name and path for us:

```python
@script(constructor="runner")
def read_artifact(an_artifact: Annotated[Path, Artifact(loader=None)]):
    print(an_artifact.read_text())
```

### `file` loader

When the loader is set to `file`, the function parameter type must be of `str` type. The variable will then contain the
contents string representation of the file stored at `path` (essentially performing `path.read_text()` automatically):

```python
@script(constructor="runner")
def read_artifact(a_file_artifact: Annotated[str, Artifact(loader=ArtifactLoader.file)]) -> str:
    return a_file_artifact
```

This loads the contents of the file to the argument `a_file_artifact` and subsequently can be used as a string inside the
function.

### `json` loader

When the loader is set to `json`, the contents of the file at `path` are read and parsed to a dictionary via `json.load`
(essentially performing `json.load(path.open())` automatically).

```python
@script(constructor="runner")
def read_dict_artifact(dict_artifact: Annotated[dict, Artifact(loader=ArtifactLoader.json)]) -> str:
    return dict_artifact["my-key"]
```

A dictionary artifact would have no validation on its contents, so having safe code relies on you knowing or manually
validating the keys that exist in it. Instead, by specifying a Pydantic type, the dictionary can be automatically
validated and parsed to that type:

```python
class MyArtifact(BaseModel):
    a = "hello "
    b = "world"


@script(constructor="runner")
def read_artifact(my_artifact: Annotated[MyArtifact, Artifact(loader=ArtifactLoader.json)]) -> str:
    return my_artifact.a + my_artifact.b
```

Under the hood, this function receives an Artifact with a JSON representation of `MyArtifact`, such as
`{"a": "hello ", "b": "world"}`. We can tell Hera to `json.load` it by setting the `loader` to `ArtifactLoader.json`,
and as the type of `my_artifact` is a `BaseModel` subclass, Hera will try to create an object from the dictionary. Then
we can use `my_artifact` as normal Python inside the function, so the function will return `"hello world"`, which will
be printed to stdout.

### Function parameter name aliasing

Script annotations can work on top of the `RunnerScriptConstructor` for name aliasing of function
parameters, in particular to allow a public `kebab-case` parameter, while using a `snake_case`
Python function parameter.

## Outputs

> Note: Output annotations are only supported when used with the `RunnerScriptConstructor`.

There are two ways to specify output Artifacts and Parameters.

### Function return annotations

Function return annotations can be used to specify the output type information for output Artifacts and Parameters, and
the function should return a value or tuple. An example can be seen
[here](../examples/workflows/scripts/script_annotations_outputs.md).

For a simple hello world output artifact example we currently have:

```python
@script(outputs=Artifact(name="hello-artifact", path="/tmp/hello_world.txt"))
def hello_world():
   with open("/tmp/hello_world.txt", "w") as f:
       f.write("Hello, world!")
```

The new approach allows us to avoid duplication of the path, which is now optional, and results in more readable code:

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

The returned values will be automatically saved in files within the Argo container according to this schema:
* `/tmp/hera-outputs/parameters/<name>`
* `/tmp/hera-outputs/artifacts/<name>`

These outputs are also exposed in the `outputs` section of the template in YAML.

The object returned from the function can be of any serialisable Pydantic type (or basic Python type) and must be
`Annotated` as an `Artifact` or `Parameter`. The `Parameter`/`Artifact`'s `name` will be used for the path of the output unless provided:
* if the annotation is an `Artifact` with a `path`, we use that `path`
* if the annotation is a `Parameter`, with a `value_from` that contains a `path`, we use that `path`

See the following two functions for specifying custom paths:

```python
@script()
def hello_world() -> Annotated[str, Artifact(name="hello-artifact", path="/tmp/hello_world_art.txt")]:
    return "Hello, world!"

@script()
def hello_world() -> Annotated[str, Parameter(name="hello-param", value_from={"path": "/tmp/hello_world_param.txt"})]:
    return "Hello, world!"
```

For multiple outputs, the return type should be a `Tuple` of Pydantic types with individual
`Parameter`/`Artifact` annotations, and the function must return a tuple from the function matching these types:

```python
@script()
def func(...) -> Tuple[
    Annotated[pydantic_type_a, Artifact(name="a", ...)],
    Annotated[pydantic_type_b, Parameter(name="b", ...)],
    Annotated[pydantic_type_c, Parameter(name="c", ...)],
]:
    return output_a, output_b, output_c
```

You may prefer to use the [Script Runner IO](script-runner-io.md#script-outputs-using-output) classes instead to avoid
long return Tuples, as return values can be set by name, rather than position.

### Input-Output function parameters

To allow users to write arbitrary `bytes` to disk, Hera allows `Parameter`/`Artifact` output to be declared as part of
the function inputs when specified as a `Path` type, allowing users to write their output to the path, rather than using
a return value. They require an additional field `output=True` to distinguish them from the input parameters and must
have an underlying `Path` type. You can use Input-Outputs alongside standard function-return outputs.

```python
@script()
def func(
    output_param: Annotated[Path, Parameter(output=True, name="my-output")]
) -> Annotated[int, Parameter(name="my-other-output", ...)]:
    output_param.write_bytes(...)

    return 42
```

The outputs directory, `/tmp/hera-outputs` by default, can be set by the user. This is done by adding:

```python
global_config.set_class_defaults(RunnerScriptConstructor, outputs_directory="user/chosen/outputs")
```
