# Advanced Hera Features

This section is used to publicize Hera's features beyond the essentials covered in the walk through. Note that these
features do not exist in Argo as they are specific to the `hera` module.

## Pre-Build Hooks

Hera offers a pre-build hook feature through `hera.shared.register_pre_build_hook` with huge flexibility to do pre-build
processing on any type of `template` or `Workflow`. For example, it can be used to conditionally set the `image` of a
`Script`, or set which cluster to submit a `Workflow` to.

To use this feature, you can write a function that takes an object of type `template` or `Workflow`, does some
processing on the object, then returns it.

For a simple example, we'll write a function that adds an annotation with key "hera", value "This workflow was submitted
through Hera!"

```py
from hera.shared import register_pre_build_hook
from hera.workflows import Workflow

@register_pre_build_hook
def set_workflow_default_labels(workflow: Workflow) -> Workflow:
    if workflow.annotations is None:
        workflow.annotations = {}

    workflow.annotations["hera-annotation"] = "This workflow was submitted through Hera!"
    return workflow

```

Now, any time `build` is called on the Workflow (e.g. to submit it or dump it to yaml), it will add in the annotation!

## Load YAML from File

Hera's `Workflow` classes offer a collection of `to` and `from` functions for `dict`, `yaml` and `file`. This
means you can load YAML files and manipulate them as Hera objects!

```py
    with Workflow.from_file("./workflow.yaml") as w:
        w.entrypoint = "my-new-dag-entrypoint"

        with DAG(name="my-new-dag-entrypoint"):
            ...  # Add some tasks!

    w.create()  # And submit to Argo directly from Hera!
```

The following are all valid assertions:

```py
with Workflow(name="w") as w:
    pass

assert w == Workflow.from_dict(w.to_dict())
assert w == Workflow.from_yaml(w.to_yaml())
assert w == Workflow.from_file(w.to_file())
```

## Submit WorkflowTemplates and ClusterWorkflowTemplates as Workflows

This feature is available for `WorkflowTemplates` and `ClusterWorkflowTemplates`, and helps you, as a dev, iterate on
your `WorkflowTemplate` until it's ready to be deployed. Calling `create_as_workflow` on a `WorkflowTemplate` will
create a `Workflow` on the fly which is submitted to the Argo cluster directly and given a generated name, meaning you
don't need to first submit the `WorkflowTemplate` itself! What this means is you don't need to keep deleting your
`WorkflowTemplate` and submitting it again, to then run `argo submit --from WorkflowTemplate/my-wt` while iterating
on your `WorkflowTemplate`.

```py
with WorkflowTemplate(
    name="my-wt",
    namespace="my-namespace",
    workflows_service=ws,
) as wt:
    cowsay = Container(name="cowsay", image="docker/whalesay", command=["cowsay", "foo"])
    with Steps(name="steps"):
        cowsay()

wt.create_as_workflow(generate_name="my-wt-test-1-")  # submitted and given a generated name by Argo like "my-wt-test-1-abcde"
wt.create_as_workflow()  # submitted and given a generated name by Argo like "my-wtabcde"
wt.create_as_workflow()  # submitted and given a generated name by Argo like "my-wtvwxyz"
```

`generate_name` is an optional parameter in case you want to control the exact value of the generated name, similarly to
the regular `Workflow`, otherwise the name of the `WorkflowTemplate` will be used verbatim for `generate_name`. The
Workflow submitted will always use `generate_name` so that you can call it multiple times in a row without naming
conflicts.

## Experimental Features

From time to time, Hera will release a new feature under the "experimental feature" flag while we develop the feature
and ensure stability. 

To enable experimental features you must set the feature by name to `True` in the `global_config.experimental_features`
dictionary before using the feature:

```py
global_config.experimental_features["NAME_OF_FEATURE"] = True
```

## Currently supported experimental features:

### `RunnerScriptConstructor`
The `RunnerScriptConstructor` found in `hera.workflows.script` and seen in the
[callable script example](../../examples/workflows/callable_script.md) is a robust way to run Python functions on Argo.
The image used by the script should be built from the source code package itself and its dependencies, so that the
source code's functions, dependencies, and Hera itself are available to run. The `RunnerScriptConstructor` is also
compatible with Pydantic so supports deserializing inputs to Python objects and serializing outputs to json strings. It
must be enabled with the `script_runner` feature flag as below.

```py
global_config.experimental_features["script_runner"] = True
```


### Script Annotations

Annotation syntax using `typing.Annotated` is supported for `Parameter`s and `Artifact`s as inputs and outputs for
functions decorated as `scripts`. They use `Annotated` as the type in the function parameters and allow us to simplify
writing scripts with parameters and artifacts that require additional fields such as a `description` or alternative
`name`.


This feature can be enabled by setting the `experimental_feature` flag `script_annotations`

```py
global_config.experimental_features["script_annotations"] = True
```

#### Parameters

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

#### Artifacts

> Note: Artifact annotations are only supported when used with the `RunnerScriptConstructor`.


The feature is even more powerful for `Artifact`s. In Hera we are currently able to specify `Artifact`s in `inputs`, but
have no way to programmatically link the given path to the code within the function:

```python
@script(inputs=Artifact(name="my-artifact", path="/tmp/file"))
def read_artifact():
    with open("/tmp/file") as a_file:  # Repeating "/tmp/file" is prone to human error!
        print(a_file.read())
```

By using annotations we can avoid repeating the `path` of the file, and your function can use the variable directly as a
`Path` object, with its value already set to the given path:

```python
@script(constructor="runner")
def read_artifact(an_artifact: Annotated[Path, Artifact(name="my-artifact", path="/tmp/file")]):
    print(an_artifact.read_text())
```

The fields allowed in the `Artifact` annotations are: `name`, `path`, and `loader`.

#### Artifact Loaders

In case you want to load an object directly from the Artifact path, we allow two types of loaders besides the default
`Path` behaviour used when no loader is specified. The `ArtifactLoader` enum provides `file` and `json` loaders.

##### `None` loader
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

##### `file` loader

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

##### `json` loader

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

##### Function parameter name aliasing

Script annotations can work on top of the `RunnerScriptConstructor` for name aliasing of function
parameters, in particular to allow a public `kebab-case` parameter, while using a `snake_case`
Python function parameter. When using a `RunnerScriptConstructor`, an environment variable
`hera__script_annotations` will be added to the Script template (visible in the exported YAML file).

#### Outputs

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
`Parameter`/`Artifact` annotations, and you should return a tuple from the function matching these types:
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
allowing users to write to the output path, without needing an explicit return. They require an additional field
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
