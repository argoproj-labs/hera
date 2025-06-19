# Hera Core Concepts

This page discusses [the core concepts of Argo Workflows](https://argoproj.github.io/argo-workflows/workflow-concepts/)
in the context of Hera.

## The `Workflow` class

The [Workflow][hera.workflows.Workflow] holds a collection of templates, and runs the
entrypoint template, usually a DAG or Steps template. In Hera, the `Workflow` is a context manager, so it loosely
mirrors the YAML dictionary structure, and adds any templates created or referenced under it.

Here is a simple "Hello World" example:

```py
from hera.workflows import Steps, Workflow, WorkflowsService, script


@script()
def echo(message: str):
    print(message)


with Workflow(
    generate_name="hello-world-",
    entrypoint="steps",
    namespace="argo",
    workflows_service=WorkflowsService(host="https://localhost:2746")
) as w:
    with Steps(name="steps"):
        echo(arguments={"message": "Hello world!"})

w.create()
```

Learn more about basics of Hera Workflows in the [walk-through](../walk-through/hello-world.md#the-workflow-context-manager)!

### The `WorkflowTemplate`

A [WorkflowTemplate](https://argo-workflows.readthedocs.io/en/latest/workflow-templates/) is a library of templates that
live on your cluster and can be referenced by other Workflows and WorkflowTemplates.

When creating a `WorkflowTemplate` in YAML, a developer would usually iterate on a `Workflow` and convert it later. Hera
allows you to start with a `WorkflowTemplate`, and create instances from it as you develop and test it.

```py
from hera.workflows import Steps, WorkflowTemplate, WorkflowsService, script


@script()
def echo(message: str):
    print(message)


with WorkflowTemplate(
    name="my-hello-world-template",
    entrypoint="steps",
    namespace="argo",
    workflows_service=WorkflowsService(host="https://localhost:2746")
) as w:
    with Steps(name="steps"):
        echo(arguments={"message": "Hello world!"})

w.create_as_workflow()  # This will create a Workflow with a name like "my-hello-world-templateaxyqb" on your cluster!
```

If you'd like to create a `Workflow` with a different name to find these iterative Workflows more easily, you can simply
pass the `generate_name` argument:

```py
w.create_as_workflow(generate_name="test-hello-world-template-")
```

This will create a `Workflow` with a name like `test-hello-world-template-lqoix` on your cluster.

## Template Classes

### Container

A container requires a name, image and command (with args if required):

```py
from hera.workflows import Container

Container(
    name="whalesay",
    image="docker/whalesay",
    command=["cowsay"],
    args=["hello world"],
)
```

### Script

Script templates are a convenience wrapper for Containers. Hera lets you write Python functions directly as Script
templates, using the `@script` decorator:

```py
from hera.workflows import script


@script()
def hello(s: str):
    print("Hello, {s}!".format(s=s))
```

Read more in the [Script decorator section](./script-basics.md#script-decorator).

### Resource

Resource templates perform operations on cluster resources directly. You can get, create, apply, delete, replace, or
patch resources.

This is the `k8s_set_owner_reference` example:

```py
from hera.workflows import Resource, Workflow

manifest = """apiVersion: v1
kind: ConfigMap
metadata:
  generateName: owned-eg-
data:
  some: value\n"""

with Workflow(
    generate_name="k8s-set-owner-reference-",
    entrypoint="k8s-set-owner-reference",
) as w:
    create_route = Resource(
        name="k8s-set-owner-reference",
        action="create",
        manifest=manifest,
        set_owner_reference=True,
    )
```

The `manifest` of a `Resource` supports passing `Workflow` objects for the
[workflow-of-workflows pattern](https://argo-workflows.readthedocs.io/en/latest/workflow-of-workflows/). This is the
`workflow_of_workflows` example:

```py
from hera.workflows import Container, Resource, Step, Steps, Workflow

with Workflow(
    generate_name="sub-workflow-,
    entrypoint="echo",
) as sub_workflow:
    Container(
        name="echo",
        image="docker/whalesay:latest",
        command=["whalesay"],
        args=["I'm in another workflow!"],
    )

with Workflow(generate_name="workflow-of-workflows-", entrypoint="main") as w:
    workflow_resource = Resource(
        name="workflow-resource",
        action="create",
        manifest=sub_workflow,
        success_condition="status.phase == Succeeded",
        failure_condition="status.phase in (Failed, Error)",
    )

    with Steps(name="main"):
        Step(name="sub-workflow", template=workflow_resource)
```

### Suspend

Suspend is a simple template that halts execution of the Workflow for a specified `duration`, or a manual resume.
Suspend templates are used for
[intermediate parameters](https://argoproj.github.io/argo-workflows/intermediate-inputs/), which in Hera are simplified
and easier to use. Read more in the [suspending guide](suspending.md)!

### Template invocators

Template invocators are used to arrange template execution order, and are templates themselves, so can in fact
recursively call themselves (ensure you have a stopping condition!).

#### Steps

Steps are created by first creating a `Steps` context, and then creating `Step` objects within it, each specifying a
template to run. By default, they run in sequence, but can run in parallel by creating a sub-context with `parallel()`.

The following is the `steps` example from the upstream examples collection:

```py
from hera.workflows import Container, Parameter, Step, Steps, Workflow

with Workflow(
    generate_name="steps-",
    entrypoint="hello-hello-hello",
) as w:
    whalesay = Container(
        name="whalesay",
        inputs=[Parameter(name="message")],
        image="docker/whalesay",
        command=["cowsay"],
        args=["{{inputs.parameters.message}}"],
    )

    with Steps(name="hello-hello-hello") as s:
        Step(
            name="hello1",
            template="whalesay",
            arguments={"message": "hello1"},
        )

        with s.parallel():
            Step(
                name="hello2a",
                template="whalesay",
                arguments={"message": "hello2a"},
            )
            Step(
                name="hello2b",
                template="whalesay",
                arguments={"message": "hello2b"},
            )
```

Functions decorated with `@script` also work in the same way under `Steps`:

```py
from hera.workflows import Steps, WorkflowTemplate, script

@script()
def echo(message: str):
    print(message)

with Workflow(
    name="hello-world-steps",
    entrypoint="steps",
) as w:
    with Steps(name="steps"):
        echo(name="echo1", arguments={"message": "Hello 1"})
        echo(name="echo2", arguments={"message": "Hello 2"})
```

Read more about `Steps` in the [walk-through](../walk-through/steps.md)!

#### DAG

A DAG is composed of Tasks with dependencies to form an acyclic graph. The syntax in Hera is similar to Steps, but with
the rshift syntax for specifying simple Task dependencies.

```py
from hera.workflows import DAG, Workflow, script

@script()
def echo(message):
    print(message)

with Workflow(generate_name="dag-diamond-", entrypoint="diamond") as w:
    with DAG(name="diamond"):
        A = echo(name="A", arguments={"message": "A"})
        B = echo(name="B", arguments={"message": "B"})
        C = echo(name="C", arguments={"message": "C"})
        D = echo(name="D", arguments={"message": "D"})
        A >> [B, C] >> D

```

Read more about `DAG`s in the [walk-through](../walk-through/dags.md)!
