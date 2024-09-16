# Advanced Hera Features

This section is used to publicize Hera's features beyond the essentials covered in the walk through. Note that these
features do not exist in Argo as they are specific to the `hera` module.

## Pre-Build Hooks

Hera offers a pre-build hook feature through `hera.shared.register_pre_build_hook` with huge flexibility to do pre-build
processing on any type of `template` or `Workflow`. For example, it can be used to conditionally set the `image` of a
`Script`, or set which cluster to submit a `Workflow` to.

To use this feature, you can write a function that takes an object of type `template` or `Workflow`, does some
processing on the object, then returns it.

For a simple example, we'll write a function that adds an annotation with a key of "hera", and value of "This workflow
was written in Hera!"

```py
from hera.shared import register_pre_build_hook
from hera.workflows import Workflow

@register_pre_build_hook
def set_workflow_default_labels(workflow: Workflow) -> Workflow:
    if workflow.annotations is None:
        workflow.annotations = {}

    workflow.annotations["hera-annotation"] = "This workflow was written in Hera!"
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
and ensure stability. Once the feature is stable and we have decided to support it long-term, it will "graduate" into
a fully-supported feature.

To enable experimental features you must set the feature by name to `True` in the `global_config.experimental_features`
dictionary before using the feature:

```py
global_config.experimental_features["NAME_OF_FEATURE"] = True
```

Note that experimental features are subject to breaking changes in future releases of the same major version. We will
usually announce changes in [the Hera slack channel](https://cloud-native.slack.com/archives/C03NRMD9KPY).

## Currently supported experimental features:

### Script Annotations

Annotation syntax using `typing.Annotated` is supported for `Parameter`s and `Artifact`s as inputs and outputs for
functions decorated as `scripts`. They use `Annotated` as the type in the function parameters and allow us to simplify
writing scripts with parameters and artifacts that require additional fields such as a `description` or alternative
`name`.

This feature can be enabled by setting the `experimental_feature` flag `script_annotations`

```py
global_config.experimental_features["script_annotations"] = True
```

Read the full guide on script annotations in [the script user guide](../user-guides/script-annotations.md).

### Script IO Models

Hera provides Pydantic models for you to create subclasses from, which allow you to more easily declare script template
inputs. Any fields that you declare in your subclass of `Input` will become input parameters or artifacts, while
`Output` fields will become output parameters artifacts. The fields that you declare can be `Annotated` as a `Parameter`
or `Artifact`, as any fields with a basic type will become `Parameters`. Turning on the `script_pydantic_io` flag will
automatically enable the `script_annotations` experimental feature.

To enable Hera input/output models, you must set the `experimental_feature` flag `script_pydantic_io`

```py
global_config.experimental_features["script_pydantic_io"] = True
```

Read the full guide on script pydantic IO in [the script user guide](../user-guides/script-runner-io.md).

### Decorators for main template types

Decorators for dags, steps and containers are provided alongside a new script decorator, letting your declare Workflows via Python functions alone.

To enable the decorators, you must install the optional extras under `experimental`

```bash
pip install hera[experimental]
```

You can then set the `experimental_feature` flag `decorator_syntax` in your code

```py
global_config.experimental_features["decorator_syntax"] = True
```

Read the full guide on decorators in [the decorator user guide](../user-guides/decorators.md).

## Graduated features

Once an experimental feature is robust and reliable, we "graduate" them to allow their use without setting the
`experimental_features` flag of the `global_config`. This comes with better support and guarantees for their feature
set. We list graduated features here so you can keep up to date.

### `RunnerScriptConstructor`

The `RunnerScriptConstructor` found in `hera.workflows.script` and seen in the
[callable script example](../examples/workflows/scripts/callable_script.md) is a robust way to run Python functions on
Argo. The image used by the script should be built from the source code package itself and its dependencies, so that the
source code's functions, dependencies, and Hera itself are available to run. The `RunnerScriptConstructor` is also
compatible with Pydantic so supports deserializing inputs to Python objects and serializing outputs to json strings.

Read [the Script Guide](../user-guides/script-basics.md#runnerscriptconstructor) to learn more!
