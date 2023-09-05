# Scripts

Scripts are an essential part of Hera's extension on top of Argo. As Hera is a Python library, Python Script templates
become the standard template, which is reflected by the greater feature set provided for writing them.

## Script Decorator

The `script` decorator function is a key offering of Hera to achieve near-native Python function orchestration. It
allows you to call the function under a Hera context manager such as a `Workflow` or `Steps` context, and it will be
treated as the intended sub-object, which would be a `template` when under a `Workflow`, or a `Step` when under a
`Steps`. The function will still behave as normal outside of any Hera contexts, meaning you can write unit tests on the
given function.

> **For advanced users**: the exact mechanism of the `script` decorator is to prepare a `Script` object within the
> decorator, so that when your function is invoked under a Hera context, the call is redirected to the `Script.__call__`
> function. This takes the kwargs of a `Step` or `Task` depending on whether the context manager is a `Steps` or a
> `DAG`. Under a Workflow itself, your function is not expected to take arguments, so the call will add the function as
> a template.

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

> **Note** in the `DAG` above, `D` will still run, even though `C` will be skipped. This is because of the `depends` logic
> resolving to `C.Succeeded || C.Skipped || C.Daemoned` due to Argo's default
> [depends logic](https://argoproj.github.io/argo-workflows/enhanced-depends-logic/#depends).

## Script Constructors

### InlineScriptConstructor

Script templates submitted to Argo typically run the given Python function in a Python image. By default, the Python
function itself is dumped to the YAML, and the Argo cluster will run that code. For the code below, we will see it
directly in the output YAML.

```py
from hera.workflows import Workflow, script

@script(add_cwd_to_sys_path=False)
def hello(s: str):
    print("Hello, {s}!".format(s=s))


with Workflow(
    generate_name="hello-world-",
    entrypoint="hello",
    arguments={"s": "world"},
) as w:
    hello()
```

We added `add_cwd_to_sys_path=False` to remove some boilerplate from the `source` below. You will see Hera adds a
`json.loads` to bridge the YAML input to a Python variable:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: hello-world-
spec:
  arguments:
    parameters:
    - name: s
      value: world
  entrypoint: hello
  templates:
  - inputs:
      parameters:
      - name: s
    name: hello
    script:
      command:
      - python
      image: python:3.8
      source: 'import json

        try: s = json.loads(r''''''{{inputs.parameters.s}}'''''')

        except: s = r''''''{{inputs.parameters.s}}''''''


        print(''Hello, {s}!''.format(s=s))'
```

This method of running the function is handled by the `InlineScriptConstructor`, called such because it constructs the
`Script` template to run the function "inline" in the YAML.

#### Importing modules

A caveat of the `InlineScriptConstructor` is that it is quite limited - as the `InlineScriptConstructor` dumps your code
to the `source` field as-is, you must also `import` (within the function itself) any modules you use in the function:

```py
@script(image="python:3.10")
def my_matcher(string: str):
    import re

    print(bool(re.match("test", string)))
```

> **Note** This also applies to other functions in your code - you will not be able to call functions defined outside of
> the scope of the script-decorated function!

If your function uses standard library imports from Python, you will be able to run your function with any standard
Python image, specified by the `image` argument of the decorator. Therefore, if you use non-standard imports, such as
`numpy`, you will need to use an image that includes `numpy`, or build your own (e.g. as a Docker image on DockerHub).

### RunnerScriptConstructor

The `RunnerScriptConstructor` is an alternative `ScriptConstructor` that uses the "Hera Runner" (think of this as being
like the PyTest Runner) to run your function on Argo. This avoids dumping the function to the `source` of a template,
keeping the YAML manageable and small, and allows you to arrange your code in natural Python fashion: imports can be
anywhere in the package, the script-decorated function can call other functions in the package, and the function itself
can take Pydantic objects as arguments. The use of the `RunnerScriptConstructor` necessitates building your own image,
as the Hera Runner runs the function by referencing it as an entrypoint of your module. The image used by the script
should be built from the source code package itself and its dependencies, so that the source code's functions,
dependencies, and Hera itself are available to run.

The `RunnerScriptConstructor` is an experimental feature and must be enabled with the `script_runner` feature flag, as
described in
[the experimental features section](../getting-started/walk-through/advanced-hera-features.md#experimental-features).

```py
global_config.experimental_features["script_runner"] = True
```

A function can set its `constructor` to `"runner"` to use the `RunnerScriptConstructor`, or use the
`global_config.set_class_defaults` function to set it once for all script-decorated functions. We can write a script
template function using Pydantic objects such as:

```py
global_config.set_class_defaults(Script, constructor="runner")

class Input(BaseModel):
    a: int
    b: str = "foo"

class Output(BaseModel):
    output: List[Input]

@script()
def my_function(input: Input) -> Output:
    return Output(output=[input])
```

This creates a template in YAML that looks like:

```yaml
- name: my-function
  inputs:
    parameters:
    - name: input
  script:
    command:
    - python
    args:
    - -m
    - hera.workflows.runner
    - -e
    - examples.workflows.callable_script:my_function
    image: my-image-with-python-source-code-and-dependencies
    source: '{{inputs.parameters}}'
```

You will notice some pecularities of this template. Firstly, it is running the `hera.workflows.runner` module, rather
than a user-module such as `examples.workflows.callable_script`. Instead, the `-e` arg specifies the `--entrypoint` to
be called by the runner, in this case the `my_function` of the `examples.workflows.callable_script` module. We do not
give a real `image` here, but we assume it exists in this example. Finally, the `source` parameter is passed the
`inputs.parameters` of the template. This is because the Hera Runner relies on a mechanism in Argo where the value
passed to `source` is dumped to a file, and then the filename is passed as the final `arg` to the `command`. Therefore,
the `source` will actually contain a list of parameters as dictionaries, which are dumped to a file which is passed to
`hera.workflows.runner`. Of course, this is all handled for you!

## Script Annotations

Annotation syntax is an experimental feature using `typing.Annotated` for `Parameter`s and `Artifact`s to declare inputs
and outputs for functions decorated as `scripts`. They use `Annotated` as the type in the function parameters and allow
us to simplify writing scripts with parameters and artifacts that require additional fields such as a `description` or
alternative `name`.

This feature must be enabled by setting the `experimental_feature` flag `script_annotations` on the global config.

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

> Note: `Artifact` annotations are only supported when used with the `RunnerScriptConstructor`.


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

In case you want to load an object directly from the `path` of the `Artifact`, we allow two types of loaders besides the
default `Path` behaviour used when no loader is specified. The `ArtifactLoader` enum provides `file` and `json` loaders.

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

There are two ways to specify output Artifacts and Parameters.

#### Function return annotations

Function return annotations can be used to specify the output type information for output Artifacts and Parameters, and
the function should return a value or tuple. An example can be seen
[here](../../examples/workflows/script_annotations_outputs).

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

For `Parameter`s we have a similar syntax:

```python
@script()
def hello_world() -> Annotated[str, Parameter(name="hello-param")]:
    return "Hello, world!"
```

The returned values will be automatically saved in files within the Argo container according to this schema:
* `/hera/outputs/parameters/<name>`
* `/hera/outputs/artifacts/<name>`

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

#### Input-Output function parameters

Hera also allows output `Parameter`/`Artifact`s as part of the function signature when specified as a `Path` type,
allowing users to write to the path as an output, without needing an explicit return. They require an additional field
`output=True` to distinguish them from the input parameters and must have an underlying `Path` type (or another type
that will write to disk).

```python
@script()
def func(..., output_param: Annotated[Path, Parameter(output=True, global_name="...", name="")]) -> Annotated[arbitrary_pydantic_type, OutputItem]:
    output_param.write_text("...")
    return output
```

The parent outputs directory, `/hera/outputs` by default, can be set by the user. This is done by adding:

```python
global_config.set_class_defaults(RunnerScriptConstructor, outputs_directory="user/chosen/outputs")
```
