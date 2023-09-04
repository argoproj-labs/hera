# Scripts

Scripts are an essential part of Hera's extension on top of Argo. As Hera is a Python library, Python Script templates
become the standard template, which is reflected by the greater feature set provided for writing them.

## Script Decorator

The `script` decorator function is a key offering of Hera in offering native Python function orchestration. It allows
you to call the function under a Hera context manager such as a `Workflow` or `Steps` context, and it will be treated as
the intended sub-object, which would be a `template` when under a `Workflow`, or a `Step` when under a `Steps`. The
function will still behave as normal outside of any Hera contexts, meaning you can write unit tests on the given
function.

> **For advanced users**: the exact mechanism of the `script` decorator is to prepare a `Script` object within the
> decoration, so that when your function is invoked under a Hera context, the call is redirected to the
> `Script.__call__` function. This takes the kwargs of a `Step` or `Task` depending on whether the context manager is a
> `Steps` or a `DAG`. Under a Workflow itself, your function is not expected to take arguments, so the call will add the
> function as a template.

When decorating a function, you should pass `Script` parameters to the `script` decorator. This includes values such as
the `image` to use, and `resources` to request.

```py
from hera.workflows import Resources, script

@script(image="python:3.11", resources=Resources(memory_request="5Gi"))
def echo(message: str):
    print(message)
```

When calling the function under a `Steps` or `DAG` context, you should pass `Step` or `Task` kwargs, such as the `name`
of the `Step`/`Task`, a `when` clause, a `with_param` list to loop over a given template, or `arguments` for the
function.

```py
with Workflow(generate_name="dag-diamond-", entrypoint="diamond") as w:
    with DAG(name="diamond"):
        A = echo(name="A", arguments={"message": "A"})
        B = echo(name="B", arguments={"message": "B"}, when=f"{A.result == 'A'}")
        C = echo(name="C", arguments={"message": "C"}, when=f"{A.result != 'A'}")
        D = echo(name="D", arguments={"message": "D"})
        A >> [B, C] >> D
```

> **Note** in the DAG above, `D` will still run, even though `C` will be skipped. This is because of the `depends` logic
> resolving to `C.Succeeded || C.Skipped || C.Daemoned` due to Argo's default
> [depends logic](https://argoproj.github.io/argo-workflows/enhanced-depends-logic/#depends).

## Script Annotations

Annotation syntax is an experimental feature using `typing.Annotated` for `Parameter`s and `Artifact`s to declare inputs
and outputs for functions decorated as `scripts`. They use `Annotated` as the type in the function parameters and allow
us to simplify writing scripts with parameters and artifacts that require additional fields such as a `description` or
alternative `name`.

This feature must be enabled by setting the `experimental_feature` flag `script_annotations` on the global config, as
described in
[the experimental features section](../getting-started/walk-through/advanced-hera-features.md#experimental-features).

```py
global_config.experimental_features["script_annotations"] = True
```

### Parameters

In Hera, we can currently specify inputs inside the `@script` decorator as follows:

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

Notice how the `name` and `default` values are duplicated for each `Parameter`. Using annotations, we can rewrite this
as:

```python
@script()
def echo_all(
    an_int: Annotated[int, Parameter(description="an_int parameter", default=1, enum=[1, 2, 3])], 
    a_bool: Annotated[bool, Parameter(description="a_bool parameter", default=True, enum=[True, False])], 
    a_string: Annotated[str, Parameter(description="a_string parameter", default="a", enum=["a", "b", "c"])]
):
    print(an_int)
    print(a_bool)
    print(a_string)
```

The fields allowed in the `Parameter` annotations are: `name`, `default`, `enum`, and `description`.

### Artifacts

> Note: Artifact annotations are only supported when used with the `RunnerScriptConstructor`.


The feature is even more powerful for `Artifact`s. In Hera we are currently able to specify `Artifact`s in `inputs`, but
the given path is not programmatically linked to the code within the function unless defined outside the scope of the
function:

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

By using annotations we can avoid repeating the `path` of the file, and the function can use the variable directly as a
`Path` object, with its value already set to the given path:

```python
@script(constructor="runner")
def read_artifact(an_artifact: Annotated[Path, Artifact(name="my-artifact", path="/tmp/file")]):
    print(an_artifact.read_text())
```

The fields allowed in the `Artifact` annotations are: `name`, `path`, and `loader`.

### Artifact Loaders

In case you want to load an object directly from the Artifact path, we allow two types of loaders besides the default
`Path` behaviour used when no loader is specified. The `ArtifactLoader` enum provides `file` and `json` loaders.

#### `None` loader
With `None` set as the loader (which is by default) in the Artifact annotation, the `path` attribute of `Artifact` is
extracted and used to provide a `pathlib.Path` object for the given argument, which can be used directly in the function
body. The following example is the same as above except for explicitly setting the loader to `None`:

```python
@script(constructor="runner")
def read_artifact(
    an_artifact: Annotated[Path, Artifact(name="my-artifact", path="/tmp/file", loader=None)]
):
    print(an_artifact.read_text())
```

#### `file` loader

When the loader is set to `file`, the function parameter type should be `str`, and will contain the contents string
representation of the file stored at `path` (essentially performing `path.read_text()` automatically):

```python
@script(constructor="runner")
def read_artifact(
    an_artifact: Annotated[str, Artifact(name="my-artifact", path="/tmp/file", loader=ArtifactLoader.file)]
) -> str:
    return an_artifact
```

This loads the contents of the file at `"/tmp/file"` to the argument `an_artifact` and subsequently can be used as a
string inside the function.

#### `json` loader

When the loader is set to `json`, the contents of the file at `path` are read and parsed to a dictionary via `json.load`
(essentially performing `json.load(path.open())` automatically). By specifying a Pydantic type, this dictionary can even
be automatically parsed to that type:

```python
class MyArtifact(BaseModel):
    a = "a"
    b = "b"


@script(constructor="runner")
def read_artifact(
    an_artifact: Annotated[MyArtifact, Artifact(name="my-artifact", path="/tmp/file", loader=ArtifactLoader.json)]
) -> str:
    return an_artifact.a + an_artifact.b
```

Here, we have a json representation of `MyArtifact` such as `{"a": "hello ", "b": "world"}` stored at `"/tmp/file"`. We
can load it with `ArtifactLoader.json` and then use `an_artifact` as an instance of `MyArtifact` inside the function, so
the function will return `"hello world"`.

#### Function parameter name aliasing

Script annotations can work on top of the `RunnerScriptConstructor` for name aliasing of function
parameters, in particular to allow a public `kebab-case` parameter, while using a `snake_case`
Python function parameter. When using a `RunnerScriptConstructor`, an environment variable
`hera__script_annotations` will be added to the Script template (visible in the exported YAML file).

### Outputs

> Note: Output annotations are only supported when used with the `RunnerScriptConstructor`.

Annotations can also be used for outputs. An example can be seen
[here](../../examples/workflows/script_annotations_outputs).

For a simple hello world output artifact example we currently have:
```python
@script(outputs=Artifact(name="hello-art", path="/tmp/hello_world.txt"))
def whalesay():
   with open("/tmp/hello_world.txt", "w") as f:
       f.write("hello world")
```

The new approach would allow us to avoid duplication of the path and result in a much more readable code.
```python
@script()
def func() -> Annotated[str, Artifact(name="hello-art", path="/tmp/hello_world.txt")]:
    return "hello world"
```

The idea is to save the returned value in a file according to this schema:
* `/hera/outputs/parameters/<name>`
* `/hera/outputs/artifacts/<name>`

The output is also exposed in the `outputs` section of the resulting yaml. 

The item returned from the function can be of any serialisable Pydantic type (or basic Python type) and needs to be
`Annotated` with an `Artifact` or `Parameter`. The `Parameter`/`Artifact`'s `name` will be taken and used for creating
the path for saving the item. If the annotation is `Artifact` and it contains a `path`, we use that `path` to save the
output. See below for examples of an output `Parameter` or `Artifact`:

Parameter output:

```python
@script()
def func(...) -> Annotated[arbitrary_pydantic_type, Parameter(name="my-output")]:
    return output  # will be saved to /hera/outputs/parameters/my-output
```

Artifact output:

```python
@script()
def func(...) -> Annotated[arbitrary_pydantic_type, Artifact(name="my-output")]:
    return output  # will be saved to /hera/outputs/artifacts/my-output
```

For multiple outputs, the return type should be a `Tuple` of arbitrary Pydantic types with individual
`Parameter`/`Artifact` annotations, and the function must return a tuple from the function matching these types:
```python
@script()
def func(...) -> Tuple[
    Annotated[arbitrary_pydantic_type_a, Artifact],
    Annotated[arbitrary_pydantic_type_b, Parameter],
    Annotated[arbitrary_pydantic_type_c, Parameter],
    ...]:
    return output_a, output_b, output_c
```

Hera also allows output `Parameter`/`Artifact`s as part of the function signature when specified as a `Path` type,
allowing users to write to the path as an output, without needing an explicit return. They require an additional field
`output=True` to distinguish them from the input parameters and must have an underlying `Path` type (or another type
that will write to disk). For `Parameters`, they will have the path of `/hera/outputs/parameters/<name>`, which can be
changed by setting the parameter's `value_from` argument. For `Artifacts`, they will have a path of
`/hera/outputs/artifacts/<name>`, which can be changed by setting the `path` of the `Artifact`.

```python
@script()
def func(..., output_param: Annotated[Path, Parameter(output=True, global_name="...", name="")]) -> Annotated[arbitrary_pydantic_type, OutputItem]:
    output_param.write_text("...")
    return output
```

The outputs directory `/hera/outputs` can be set by the user. This is done by adding:

```python
global_config.set_class_defaults(RunnerScriptConstructor, outputs_directory="user/chosen/outputs")
```

in the script using the outputs. Note, this is only done for scripts using the runner constructor.
