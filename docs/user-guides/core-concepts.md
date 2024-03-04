# Hera Core Concepts

This page discusses [the core concepts of Argo Workflows](https://argoproj.github.io/argo-workflows/workflow-concepts/)
in the context of Hera.

## The `Workflow` class

The main resource in Argo, and the key class of Hera, the [Workflow](../api/workflows/hera.md#hera.workflows.Workflow) is
responsible for holding your templates, setting an entrypoint and running the templates. In Hera, the `Workflow`
implements the context manager interface, so it loosely mirrors the YAML dictionary structure and as we are using a
Python class, there are fewer fields you need to specify, such as the `apiVersion` and `kind` seen in YAML. The
structure of the Workflow comes from the [template](#template-classes) objects instantiated within its context.

See the `hello_world.py` example below:

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

In Hera, the [WorkflowTemplate](../api/workflows/hera.md#hera.workflows.WorkflowTemplate) is a subclass of `Workflow`,
so [in a similar way to Argo](https://argoproj.github.io/argo-workflows/workflow-templates/#workflowtemplate-spec), it
can be a drop-in replacement of your `Workflow`. Usually in YAML, you would need to change the `kind` and set
`generateName` instead of `name`. However, for this developer workflow of iterating on a `Workflow` to eventually create
a `WorkflowTemplate`, we provide a simple `create_as_workflow` convenience function, which will submit your
`WorkflowTemplate` as a `Workflow` to Argo, using generate_name automatically.

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

If you'd like to create your `Workflow` with a different name to find these iterative Workflows more easily, you can
simply pass the `generate_name` argument:

```py
w.create_as_workflow(generate_name="test-hello-world-template-")
```

This will create a `Workflow` with a name like "test-hello-world-template-lqoix" on your cluster.

## Template Classes

Hera mirrors the 6 template types from Argo.

### Container

A container requires a name, image and command (with args if required):

```py
from hera.workflows import Container

Container(name="whalesay", image="docker/whalesay", command=["cowsay"], args=["hello world"])
```

### Script

With the Script template being a conveninece wrapper around a Container, Hera builds on this foundation to provide
Python-functions-as-scripts directly as templates. It promotes Scripts to the second-most-important feature behind
Workflows themselves, with extensive support for writing templates easily. The most basic script template can be a
function as follows, decorated with `@script`.

```py
from hera.workflows import script


@script()
def hello(s: str):
    print("Hello, {s}!".format(s=s))
```

Read more in the [Script decorator section](./script-basics.md#script-decorator).


### Resource

Performs operations on cluster Resources directly. It can be used to get, create, apply, delete, replace, or patch
resources on your cluster. Hera's support for generic Resources is currently limited, but a Workflow-like Hera object
can be passed in to the `manifest` parameter.

This first example is the `k8s_set_owner_reference` example:

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

This next example shows a simple example of passing a `Workflow` directly to `manifest`, seen in the
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
and easier to use. Read more in the [suspending walk-through](../walk-through/suspending.md)!


## Template invocators

Template invocators to arrange templates, and are templates themselves, so can in fact recursively call themselves.

### Steps

In Hera, Steps consist of a series of Steps, each specifying a template to run, with a `parallel()` feature on a `Steps`
object to run sub-steps in parallel. The following is the `steps` example from the upstream examples collection.

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


### DAG

A DAG is composed of Tasks with dependencies to form an acyclic graph. The syntax in Hera is similar to Steps, but with
the rshift convenience syntax for specifying simple Task dependencies. Read more at 

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

Read more about `DAG`s in the [walk-through](../walk-through/dag.md)!
