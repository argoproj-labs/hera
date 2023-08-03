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

### Currently supported experimental features:

#### `RunnerScriptConstructor`
The `RunnerScriptConstructor` found in `hera.workflows.script` and seen in the
[callable script example](../../examples/workflows/callable_script.md) is a robust way to run Python functions on Argo.
The image used by the script should be built from the source code package itself and its dependencies, so that the
source code's functions, dependencies, and Hera itself are available to run. The `RunnerScriptConstructor` is also
compatible with Pydantic so supports deserializing inputs to Python objects and serializing outputs to json strings. It
must be enabled with the `script_runner` feature flag as below.

```py
global_config.experimental_features["script_runner"] = True
```


#### Script Annotations
Annotations are supported for input `Parameter`s and `Artifact`s. They can be added using `typing.Annotated` in the function parameters. 

```python
@script()
def func(a_param: Annotated[str, Parameter(name="a-param", default="param")]):
    ...
```

This allows us to simplify writing scripts with parameters and artifacts that require additional fields. 

##### Parameters

In normal Hera, we can specify inputs inside the `@script` decorator as follows:

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

Notice how `Parameter` `name`s and `default` values are duplicated. Using annotations, we can do:

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

##### Artifacts

The improvement is even more noticeable for `Artifact`s. In old Hera we have:

```python
@script(inputs=Artifact(name="my-artifact", path="/tmp/file"))
def read_artifact():
    with open("/tmp/file") as a_file:
        print(a_file.read())
```

and with annotations we can do:

```python
@script()
def read_artifact(an_artifact: Annotated[Path, Artifact(name="my-artifact", path="/tmp/file")]):
    print(an_artifact.read_text())
```

The path duplication is no longer necessary since `an_artifact` is a `Path` object.

The fields allowed in the `Artifact` annotations are: `name`, `path`, and `loader`.

For `Artifact`s, we allow three types of loaders. Using `ArtifactLoader`, we have `file`, `json`, 
and `None`.

With no loader, the `path` attribute of `Artifact` is extracted and can be subsequently used in 
the function body by referring to the function parameter. This can be seen above.

When the loader is set to `file`, the function parameter will be the contents of the file 
stored at `path`. When the loader is set to `json`, the contents of the file at `path` are 
read and parsed to `json`.

Script annotations can work on top of the `RunnerScriptConstructor` for name aliasing of function
parameters, in particular to allow a public `kebab-case` parameter, while using a `snake_case`
Python function parameter. When using a `RunnerScriptConstructor`, an environment variable
`hera__script_annotations` will be added to the Script template.
Script annotations also work with the regular `InlineScriptConstructor` for
generating valid template parameters in the yaml instead of adding them in the `@script` decorator.

This feature can be enabled by setting the `experimental_feature` flag `script_annotations`

```py
global_config.experimental_features["script_annotations"] = True
```
