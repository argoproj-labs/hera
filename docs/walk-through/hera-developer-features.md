# Hera Developer Features

Here we showcase more features that help developers write Workflows in Hera. Note that these features do not exist in
Argo as they are specific to Hera, being a Python library.

## Set Class Defaults

You are able to set basic default values for any attributes in Hera's custom classes, such as `Script`, `Container` and
`Workflow`, by using `hera.shared.global_config.set_class_defaults`. You pass the class you want to set defaults on, and
then kwargs for all the attributes you want to set (with their respective values). For example, if you wanted to set some
default values for any `Container` objects you create, you would do:

```py
from hera.shared import global_config
from hera.workflows import Container

global_config.set_class_defaults(
    Container,
    image="my-image:latest",
    image_pull_policy="Always",
    command=["cowsay"],
)
```

And then use the `Container` class in your Workflows as normal, but now the `Container` will have pre-populated default
attributes when created:

```py
with Workflow(name="w") as w:
    do_a_cowsay = Container(name="cowsay-container", args=["Hello, world!"])
    with Steps(name="steps"):
        do_a_cowsay()
```

Notice how we do not need to set `image` or `command`!

## Pre-Build Hooks

If [class defaults](#set-class-defaults) don't meet your needs, Hera also offers a pre-build hook feature through
`hera.shared.register_pre_build_hook` with huge flexibility to do pre-build processing on any type of `template` or
`Workflow`. For example, it can be used to conditionally set the `image` of a `Script`, or set which cluster to submit a
`Workflow` to.

To use this feature, you can write a function that takes an object of type `template` or `Workflow`, does some
processing on the object, then returns it.

For a simple example, we'll write a function that adds an annotation with a key of "hera-annotation", and value of "This
workflow was written in Hera!"

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
