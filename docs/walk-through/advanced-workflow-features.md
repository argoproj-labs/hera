# Advanced Workflow Features

This section exemplifies Workflow features found in Argo, but are beyond the scope of the Walk Through.

## Workflow-Level Lifecycle Hooks

Lifecycle hooks are typically used to run a given template, according to the given condition, such as on workflow exit,
or when the workflow has a `Running` status.

* [Read more about Lifecycle Hooks on the Argo docs](https://argoproj.github.io/argo-workflows/lifecyclehook/)
* [See the Workflow-level lifecycle hook example](../examples/workflows/upstream/life_cycle_hooks_wf_level.md)

## Exit Handlers (deprecated)

Exit handlers are templates that always execute (regardless of success or failure) at the end of a workflow. They were
replaced by workflow-level ([above](#workflow-level-lifecycle-hooks)) and [template-level hooks](./advanced-template-features.md#lifecycle-hooks).

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

See the [Empty Volume](../examples/workflows/upstream/volumes_emptydir.md) example for creating a volume dynamically for the Workflow, or the [Existing Volumes](../examples/workflows/upstream/volumes_existing.md) example for using an existing volume.
