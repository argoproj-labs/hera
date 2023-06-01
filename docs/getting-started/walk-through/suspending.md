# Suspending Workflows

Hera makes creating `suspend` templates in your workflow a breeze.

# Basic `suspend` Usage

If you want to pause your Workflow for a certain duration you can create a `Suspend` template, which can slot in
anywhere in your `Steps` or `DAG` context. The only import  you need on top of the Hello World example is
`hera.workflows.Suspend`:

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
        echo(arguments={"message": "The next node will suspend for 10 seconds"})
        suspend_template(name="suspend")
        echo(arguments={"message": "Finished waiting!"})
```
