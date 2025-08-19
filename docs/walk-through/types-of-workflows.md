# Types of Workflows

Argo Workflows provides 4
[Custom Resources](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/), which in turn
are classes provided by Hera:

* The `Workflow`, which we have seen throughout the examples already. It is the "live" object on the Kubernetes cluster
  containing a current "run".
* The `CronWorkflow`: a `Workflow` that will repeatedly run according to a
  [cron schedule](https://en.wikipedia.org/wiki/Cron).
* The `WorkflowTemplate`: a collection of modular, reusable `templates` which you use in other Workflows. It is
  only available in the Kubernetes namespace that it is added to.
* The `ClusterWorkflowTemplate`: the same as a `WorkflowTemplate` but available across all namespaces in the cluster.

In Hera, these all follow the same basic structure and features of `Workflow`, being subclasses of it. We will explain some of the key differences and unique features below.


## `CronWorkflows`

It is often useful to define a `Workflow` that will repeatedly run. We can use a `CronWorkflow` to handle this for us.
Given a `Workflow`, we can easily convert it to a `CronWorkflow` by changing the class, changing `generate_name` to a
suitable `name`, and then filling out the special cron fields, which at a minimum includes the `schedules` field:

```py
from hera.workflows import CronWorkflow, script


@script()
def hello(s: str):
    print("Hello, {s}!".format(s=s))


with CronWorkflow(
    name="hello-world-cron",
    entrypoint="hello",
    arguments={"s": "world"},
    schedules=[
        "*/2 * * * *",  # Run every 2 minutes
    ],
) as w:
    hello()
```

When you call `w.create()` on a `CronWorkflow`, it will *not* immediately run; it will only run at the times specified by
the schedule. If you want to create a new CronWorkflow but not start running it on the schedule, you can pass
`cron_suspend=True`, which will let you toggle it on later in the UI or CLI:

```py
with CronWorkflow(
    name="hello-world-cron",
    entrypoint="hello",
    arguments={"s": "world"},
    schedules=[
        "*/2 * * * *",  # Run every 2 minutes
    ],
    cron_suspend=True,
) as w:
    hello()
```

!!! warning

    Trying to run `w.create()` on a `CronWorkflow` that already exists on the cluster will raise a
    `hera.exceptions.AlreadyExists` exception. You can use `w.update()` to replace the `CronWorkflow` of the same name.
    You may find a Continuous Deployment tool like [ArgoCD](https://argo-cd.readthedocs.io/en/stable/) helpful to manage
    CronWorkflows.

Learn about all the available `CronWorkflow` fields and what they do in the
[Argo docs](https://argo-workflows.readthedocs.io/en/latest/fields/#cronworkflowspec)!

## `WorkflowTemplates` and `ClusterWorkflowTemplates`

`WorkflowTemplates` and `ClusterWorkflowTemplates` should be defined using a `name`, instead of a `generate_name`:

```py
from hera.workflows import (
    ClusterWorkflowTemplate,
    WorkflowTemplate,
    script,
)
from hera.workflows.models import TemplateRef


@script()
def hello(s: str):
    print("Hello, {s}!".format(s=s))


with WorkflowTemplate(name="hello-world-workflow-template", namespace="argo") as wt:
    hello()

with ClusterWorkflowTemplate(name="hello-world-cluster-workflow-template") as cwt:
    hello()
```

There is no practical difference when defining a `WorkflowTemplate` versus a `ClusterWorkflowTemplate`; it only matters
for whether you want the `WorkflowTemplate` available in particular namespaces, or across all namespaces in the cluster.

!!! note

    Due to their similarity, when we refer to `WorkflowTemplates` throughout the rest of the documentation, we are
    implicitly referring to `ClusterWorkflowTemplates` as well.

You can upload `WorkflowTemplates` and `ClusterWorkflowTemplates` to the cluster through `wt.create()` or `cwt.create()`
in the above example.

!!! warning

    Trying to run `create()` on a `WorkflowTemplate` that already exists on the cluster will raise a
    `hera.exceptions.AlreadyExists` exception. You can use `w.update()` to replace the `WorkflowTemplate` of the same
    name. You may find a Continuous Deployment tool like [ArgoCD](https://argo-cd.readthedocs.io/en/stable/) helpful to
    manage WorkflowTemplates, or read more about versioning WorkflowTemplates in the
    [Best Practices](../user-guides/best-practices.md#versioning) guide!

### Using `WorkflowTemplates` and `ClusterWorkflowTemplates` Through `TemplateRefs`

Once you have a `WorkflowTemplate` or `ClusterWorkflowTemplates`, you can upload it to the cluster through `w.create()`.
Then, you can use it in other `Workflows`, `WorkflowTemplates` or `CronWorkflows` by using a
`hera.workflows.models.TemplateRef` in a `Step` or `Task`. You will need to specify `cluster_scope=False` for
`WorkflowTemplates`, and `cluster_scope=True` for `ClusterWorkflowTemplates`.

```py
with Workflow(
    generate_name="use-workflow-templates-",
    entrypoint="steps",
    namespace="argo",
) as w:
    with Steps(name="steps"):
        Step(
            name="hello-template-ref",
            template_ref=TemplateRef(
                name="hello-world-workflow-template",
                template="hello",
                cluster_scope=False,
            ),
            arguments={"s": "this is using a WorkflowTemplate"},
        )
        Step(
            name="hello-cluster-template-ref",
            template_ref=TemplateRef(
                name="hello-world-cluster-workflow-template",
                template="hello",
                cluster_scope=True,
            ),
            arguments={"s": "this is using a ClusterWorkflowTemplate"},
        )
```

See the full runnable code in the [Template Refs example](../examples/workflows/misc/template_refs.md)!
