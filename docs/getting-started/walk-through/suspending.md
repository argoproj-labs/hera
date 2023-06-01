# Suspending Workflows

A user can pause execution of a Workflow at any time through Argo CLI using `argo suspend WORKFLOW`, and resumed by
`argo resume WORKFLOW`, or in the Argo UI. Alternatively, you can automatically suspend a Workflow at specific points
using `Suspend` templates.

Hera makes creating `Suspend` templates in your workflow a breeze!

## Basic `Suspend` Usage

If you want to pause your Workflow you can create a `Suspend` template, which can slot in anywhere in your `Steps` or
`DAG` context. The only import you need on top of the Hello World example is `hera.workflows.Suspend`:

```py
from hera.workflows import Steps, Suspend, Workflow, script


@script()
def echo(message: str):
    print(message)


with Workflow(
    generate_name="suspending-workflow-",
    entrypoint="steps",
) as w:

    suspend_template = Suspend(name="wait-for-resume")

    with Steps(name="steps"):
        echo(arguments={"message": "The next node waits until you resume the workflow"})
        suspend_template(name="suspend")
        echo(arguments={"message": "Finished waiting!"})
```

## Timed `Suspend` Usage

If instead you want to pause the Workflow for a specific length of time, you can simply pass a value to the `Suspend`
template's `duration` variable.

```py
from hera.workflows import Steps, Suspend, Workflow, script


@script()
def echo(message: str):
    print(message)


with Workflow(
    generate_name="suspending-workflow-",
    entrypoint="steps",
) as w:

    suspend_template = Suspend(name="wait-10-seconds", duration=10)

    with Steps(name="steps"):
        echo(arguments={"message": "The next node will wait for 10 seconds"})
        suspend_template(name="suspend")
        echo(arguments={"message": "Finished waiting!"})
```

## Intermediate Parameters

[Intermediate Parameters](https://argoproj.github.io/argo-workflows/intermediate-inputs/) is an Argo UI feature that
pauses a Workflow to wait for user inputs. Hera makes Suspend templates using Intermediate Parameters very easy to
create.

Let's create a Workflow to suspend indefinitely, waiting for user input, and echo the user's input in the next `Step`.

```py
@script()
def echo(message: str):
    print(message)


with Workflow(
    generate_name="intermediate-parameter-workflow-",
    entrypoint="steps",
) as w:

    suspend_template = Suspend(
        name="suspend-with-intermediate-param",
        intermediate_parameters=[Parameter(name="my-message", default="")],
    )

    with Steps(name="steps"):
        suspend_step = suspend_template(name="suspend")
        echo(arguments={"message": suspend_step.get_parameter("my-message")})
```

We can also use enums in the same way shown in the Argo example:

```py
@script()
def deploy():
    print("Deploying!")


with Workflow(
    generate_name="approval-workflow-",
    entrypoint="steps",
) as w:

    approval_template = Suspend(
        name="approval",
        intermediate_parameters=[Parameter(name="approve", default="NO", enum=["YES", "NO"])],
    )

    with Steps(name="steps"):
        approval = approval_template(name="suspend")
        deploy(when=f'{approval.get_parameter("approve")} == "YES"')
```
