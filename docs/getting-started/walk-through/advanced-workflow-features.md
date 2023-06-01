# Advanced Workflow Features

This section is used to publicize Workflow features beyond the essentials covered in the walk through.

## Pre-Build Hooks

Hera offers a pre-build hook feature through `hera.shared.register_pre_build_hook` with huge flexibility to do pre-build
processing on any type of `template` or `Workflow`. For example, it can be used to conditionally set the `image` of a
`Script`, or set which cluster to submit a `Workflow` to.

To use this feature, write a function that takes the `template` or `Workflow` type, processes it, then returns it. For a
simple example, we'll write a function that adds an annotation with key "hera", value "This workflow was submitted
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

## Experimental Features

## Exit Handlers

## Volume Claim Templates