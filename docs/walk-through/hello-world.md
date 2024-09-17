# Hello World

Let's take a look at the `hello_world.py` from the [Quick Start](./quick-start.md) guide.

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

## The imports

As we are using Argo Workflows, we import specialized classes from `hera.workflows`. You will see Argo concepts from the
Argo spec have been transformed into powerful Python classes, explore them at the
[Hera Workflows API reference](../api/workflows/hera.md).


## Using **Any Function** on Argo

For this Workflow, we want to echo using Python's `print` function, which is wrapped in our convenience `echo` function
so that we can decorate it. We use Hera's `script` decorator to turn the `echo` function into what's known as a
[Script template](https://argoproj.github.io/argo-workflows/workflow-concepts/#script), and is mirrored in Hera with the
`Script` class. As we're defining the Workflow in Python, Hera is able to infer multiple field values that the developer
would otherwise have to define when using YAML.

> **Note:** Using Hera's defaults for the script decorator is only suitable for very small/basic functions as it will
> not allow you to use functions or modules defined outside of the function. For the best experience you will need to
> build your own image and set up your config to use the `RunnerScriptConstructor`.
> [See the Script Basics guide for details](../user-guides/script-basics.md).

### The `script` Decorator

The `script` decorator can take kwargs that a `Script` can take. Importantly, you can specify the `image` of Python
to use instead of the default `python:3.9` for your script if required:

```py
@script(image="python:3.11")
def echo(message: str):
    print(message)
```

Alternatively, you can specify this image once via the `global_config.image` variable, and it will be used for all
`script`s automatically:

```py
from hera.shared import global_config
global_config.image = "python:3.11"

@script()  # "echo" will now run using python:3.11, as will any other scripts you define
def echo(message: str):
    print(message)

@script()  # "echo_twice" will also run using python:3.11
def echo_twice(message: str):
    print(message)
    print(message)
```

For an in-depth explanation of the mechanics of the script decorator, see the
[script decorator section](../user-guides/script-basics.md#script-decorator) in the scripts user guide, and read about
building your own image in the [script constructors section](../user-guides/script-basics.md#script-constructors).

## The Workflow Context Manager

The Workflow context manager acts as a scope under which `template` Hera objects can be declared, which include
Containers, Scripts, DAGs [and more](https://argoproj.github.io/argo-workflows/workflow-concepts/#template-types). For a
minimal example, you will need to provide your `Workflow` the initialization values as seen

```py
with Workflow(
    generate_name="hello-world-",
    entrypoint="steps",
    namespace="argo",
    workflows_service=WorkflowsService(host="https://localhost:2746")
) as w:
```

* `generate_name` is taken by Argo upon submission, where it appends a random 5 character suffix, so you may see this
  Workflow run with a name like `hello-world-vmsz5`.
* `entrypoint` tells Argo which template to run upon submission.
* `namespace` refers to the Kubernetes namespace you want to submit to.
* `workflows_service` is the submission service.

## The Steps Context Manager

A `Steps` template is the second template type of this example, the first being the `Script`. The `Steps` template,
along with the `DAG` template, is known as a "template invocator". This is because they are used to arrange other
templates, mainly Containers and Scripts, to do the actual work. In Hera, the `Steps` class is a context manager as it
automatically arranges your templates in the order that you add them, with each template invocation known as a `Step`.

```py
with Steps(name="steps"):
```

To invoke the `echo` template, you can call it, passing values to its arguments through the `arguments` kwarg, which is
a dictionary of the _function_ kwargs to values. This is because under a `Steps` or `DAG` context manager, the `script`
decorator converts a call of the function into a `Step` or `Task` object, to which you must pass `Step` or `Task`
initialization kwargs.

```py
echo(arguments={"message": "Hello world!"})
```

## Submitting the Workflow

Finally, with the workflow defined, the actual submisson occurs on

```py
w.create()
```

This uses the `WorkflowsService` to submit to Argo using its REST API, so `w.create()` can be thought of as running
`argo submit`.

Alternatively, you may want to see what the YAML looks like for this Workflow, which can be done with a print or to a
file using `w.to_yaml()`.

```py
print(w.to_yaml())
```
