# Advanced Workflow Features

This section exemplifies features found in Argo, but are beyond the scope of the Walk Through.

## Exit Handlers

Exit handlers are templates that always execute (regardless of success or failure) at the end of a workflow.

Some use cases listed from [Argo Workflows](https://argoproj.github.io/argo-workflows/walk-through/exit-handlers/)
include:

* cleaning up after a workflow runs
* sending notifications of workflow status (e.g. e-mail/Slack)
* posting the pass/fail status to a web-hook result (e.g. GitHub build result)
* resubmitting or submitting another workflow

To use an exit handler on a Workflow in Hera, you can either define the template to use within the workflow, then set
the `on_exit` member which will take the name from the template itself, or specify the template to use as a string when
initializing the Workflow object. See both methods below.

```py
with Workflow(
    generate_name="exit-handler-workflow-",
) as w1:
    cleanup_exit_handler = Container(
        name="cleanup",
        image="docker/whalesay",
        command=["cowsay"],
        args=["cleanup!"],
    )
    w1.on_exit = cleanup_exit_handler
    ...

with Workflow(
    generate_name="exit-handler-workflow-",
    on_exit="cleanup",
) as w2:
    cleanup_exit_handler = Container(
        name="cleanup",
        image="docker/whalesay",
        command=["cowsay"],
        args=["cleanup!"],
    )
    ...
```

## Volume Claim Templates

Volume Claim Templates can be used to copy a large amount data from one step to another in a Workflow.

See the [Empty Volume](../../examples/workflows/upstream/volumes_emptydir.md) example for creating a volume dynamically for the Workflow, or the [Existing Volumes](../../examples/workflows/upstream/volumes_existing.md) example for using an existing volume.
