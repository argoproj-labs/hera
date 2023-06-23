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
and ensure stability. Currently this is used for the `RunnerScriptConstructor` seen in the
[runner script example](../../examples/workflows/callable_script.md).

To enable experimental features you must set the feature by name to `True` in the `global_config.experimental_features`
dictionary before using the feature:

```py
global_config.experimental_features["script_runner"] = True
```
