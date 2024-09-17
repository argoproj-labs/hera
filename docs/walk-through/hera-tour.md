# Hera Tour-torial

## Building the DAG diamond from scratch

> This tutorial is a written, in-depth version of the ArgoCon EU 2024 talk - "Orchestrating Python Functions Natively
> with Hera", [watch it here](https://www.youtube.com/watch?v=4G3Q6VMBvfI&list=PLj6h78yzYM2NA4NbSC6_mQNza2r3WV87h&index=4)!

Let's go through some features of Hera by building a Workflow that will initially implement the DAG diamond example.

First, with your Python environment set up, we need to install `hera`:

```
pip install hera
```

Then, open a new file for our Workflow. Let's make a function that echoes the input message:

```py
def echo(message):
    print(message)
```

In Hera, we can declare a function as a "Script" template using the `@script` decorator:

```py
from hera.workflows import script

@script()
def echo(message):
    print(message)
```

This makes `echo` an inline script function, which means when submitted to Argo Workflows as part of a Workflow, you
will see the function body dumped into the `source` of the Script template, which is written in YAML (a superset of JSON):

```yaml
  - name: echo
    inputs:
      parameters:
      - name: message
    script:
      command:
      - python
      image: python:3.9
      source: |-
        import json
        try: message = json.loads(r'''{{inputs.parameters.message}}''')
        except: message = r'''{{inputs.parameters.message}}'''

        print(message)
```

But wait, where did `image: python:3.9` come from? It's a default value for the `image` of a script-decorated function
in Hera. Let's update that to a more recent version of Python in the decorator:

```py
from hera.workflows import script

@script(image="python:3.12")
def echo(message):
    print(message)
```

You'll also notice the use of the `json` built-in module to load the parameter in the `source`. This is so Python can
try to load the string value from the YAML to a valid JSON type (otherwise using the raw string). This is possible
because YAML is a superset of JSON, so for a single value, it should be valid JSON.


Next, we need a Workflow to hold the `DAG` that we want to create. We do this with the `Workflow` class from
`hera.workflows`. We'll use `generate_name` to tell Argo to create a unique suffix appended to the given string each
time we submit the Workflow.

```py
from hera.workflows import Workflow, script

@script(image="python:3.12")
def echo(message):
    print(message)

with Workflow(generate_name="dag-diamond-") as w:
    ...
```

We've created the `Workflow` as a context manager, which means any templates we reference or create within the context
will be added automatically to the Workflow.

In Argo Workflows, a DAG is itself a template that is made up of Tasks that run other templates. In Hera, we create a
DAG using the `DAG` class from `hera.workflows`, using it as a context manager. We can also specify the DAG as the
`entrypoint` of the workflow:

```py
from hera.workflows import DAG, Workflow, script

@script(image="python:3.12")
def echo(message):
    print(message)

with Workflow(generate_name="dag-diamond-", entrypoint="diamond") as w:
    with DAG(name="diamond"):
        ...
```

The DAG context manager will add any `Task` created within its context to the graph. The `Task` class, imported from
`hera.workflows` requires a `name`, and one of a `template` or a `template_ref` (more on that later). Let's create some
tasks! We can pass arguments to the echo template used by each `Task` in a dictionary to the `arguments` kwarg of the
`Task`.

```py
from hera.workflows import DAG, Task, Workflow, script

@script(image="python:3.12")
def echo(message):
    print(message)

with Workflow(generate_name="dag-diamond-", entrypoint="diamond") as w:
    with DAG(name="diamond"):
        A = Task(name="A", template=echo, arguments={"message": "A"})
        B = Task(name="B", template=echo, arguments={"message": "B"})
        C = Task(name="C", template=echo, arguments={"message": "C"})
        D = Task(name="D", template=echo, arguments={"message": "D"})
```

We now have 4 `Tasks`, but we have not declared any dependencies between the tasks, which means they will all run in
parallel! Remember, we are trying to create a diamond. To declare dependencies, we use the rshift syntax, which also
allows you to use Python lists of Tasks in places. Let's create the diamond!

```py
from hera.workflows import DAG, Task, Workflow, script

@script(image="python:3.12")
def echo(message):
    print(message)

with Workflow(generate_name="dag-diamond-", entrypoint="diamond") as w:
    with DAG(name="diamond"):
        A = Task(name="A", template=echo, arguments={"message": "A"})
        B = Task(name="B", template=echo, arguments={"message": "B"})
        C = Task(name="C", template=echo, arguments={"message": "C"})
        D = Task(name="D", template=echo, arguments={"message": "D"})
        A >> [B, C] >> D
```

This means A will run first as it has no dependencies, then B and C will run in parallel once A completes, and finally
once both B and C complete, D will run.

Now, we want to actually submit this workflow! You'll need to use the right authorization for your cluster, but for now,
assuming a `localhost`, we can submit the workflow by passing a `WorkflowsService` to the `Workflow` and calling
`w.submit()`.

```py
from hera.workflows import DAG, Task, Workflow, WorkflowsService, script

@script(image="python:3.12")
def echo(message):
    print(message)

with Workflow(
    generate_name="dag-diamond-",
    entrypoint="diamond",
    namespace="argo",
    workflows_service=WorkflowsService(host="https://localhost:2746"),
) as w:
    with DAG(name="diamond"):
        A = Task(name="A", template=echo, arguments={"message": "A"})
        B = Task(name="B", template=echo, arguments={"message": "B"})
        C = Task(name="C", template=echo, arguments={"message": "C"})
        D = Task(name="D", template=echo, arguments={"message": "D"})
        A >> [B, C] >> D

w.submit()
```

Now, you can write and submit Workflows that use DAG and Script templates!

## Syntactic Sugar

If you want to save on some typing, you can use the name of the function in place of `Task`, which looks like:

```py
from hera.workflows import DAG, Workflow, WorkflowsService, script

@script(image="python:3.12")
def echo(message):
    print(message)

with Workflow(
    generate_name="dag-diamond-",
    entrypoint="diamond",
    namespace="argo",
    workflows_service=WorkflowsService(host="https://localhost:2746"),
) as w:
    with DAG(name="diamond"):
        A = echo(name="A", arguments={"message": "A"})
        B = echo(name="B", arguments={"message": "B"})
        C = echo(name="C", arguments={"message": "C"})
        D = echo(name="D", arguments={"message": "D"})
        A >> [B, C] >> D

w.submit()
```

This syntax means we don't need to specify the template being used anymore, or use the `Task` class directly. The return
values from the function calls are still `Tasks` though!

> **Note** Currently, this syntax is not understood by Mypy, so you may see linting errors, in which case you can use
> `cast` from `typing`, or tell your Mypy linter to ignore those lines.

## Type Safe Functions

So far, the `echo` function doesn't make use of type annotations or return values, which makes it much harder to test.
So, if you want to write type-safe functions and return values, you'll need the Hera Runner! This is a feature that can
be enabled by setting the script's `constructor` field, or setting the `RunnerScriptConstructor` as the default in the
`global_config` to use it for all your scripts:

```py
from hera.shared import global_config
from hera.workflows import Script, RunnerScriptConstructor

global_config.set_class_defaults(Script, constructor=RunnerScriptConstructor())
```

> When you use the Hera Runner, you need to build your code into a hosted image that your Argo instance can pull! You can then set the `global_config.image`:
> ```py
> global_config.image = "my-built-python-image"
> ```

Now we can write a function with parameters that use type hints! Let's calculate the area of a given rectangle's length
and width:

```py
from hera.workflows import script

@script(constructor="runner", image="my-built-python-image")
def calculate_area_of_rectangle(length: float, width: float):
    print(length * width)
```

Notice how we now use `float` as the type hint of the inputs. The Hera Runner will raise a Pydantic validation error if
passed a string that cannot be deserialized into a float - e.g. `"hello"` will raise an error, but not `"1"`. This is
because Hera uses `validate_arguments` (for Pydantic v1 installations) or `validate_call` (for Pydantic v2
installations) when calling the function.

What if we wanted to use classes in the types in the inputs? Before we jump into adding classes, we must keep in mind
we'll be running this function on Argo, where the inputs are coming from the YAML definition. So we need a way to
deserialize inputs strings into the classes. Lucky for us, Pydantic is able to deserialize JSON-serialized strings into
Python objects, and as we've mentioned, the Hera Runner integrates with Pydantic!

## Pydantic-Powered Functions

The Hera Runner inspects the types of your function's parameters, and for any type that inherits from Pydantic's
`BaseModel`, the Hera Runner will try to deserialize the JSON input string into an object of that type. Therefore we can
create a class inheriting from `BaseModel`, which lets Hera deserialize the input into an object, and lets us use
convenience functions on that object, such as an `area()` function. Let's try it out!

```py
from pydantic import BaseModel

class Rectangle(BaseModel):
    length: float
    width: float

    def area(self) -> float:
        return self.length * self.width

@script(constructor="runner", image="my-built-python-image")
def calculate_area_of_rectangle(rectangle: Rectangle):
    print(rectangle.area())
```

But we've still got that pesky `print` statement. We should return the value of the area instead! When running on Argo,
the Hera Runner will print the return value to stdout, so you can still use the `.result` of the previous step or task
as before.

```py
@script(constructor="runner", image="my-built-python-image")
def calculate_area_of_rectangle(rectangle: Rectangle) -> float:
    return rectangle.area()

```

Now we can test this function - acting as a script template - in isolation outside of Argo!

```py
def test_calculate_area_of_rectangle():
    r = Rectangle(length=2.0, width=3.0)
    assert calculate_area_of_rectangle(r) == 6.0
```

Awesome!

## Workflow Testing

So, we can test individual templates, what about the whole workflow? Well, good news! Using Hera's YAML to Python
deserializing, we can inspect the `status` of the `Workflow` returned from the workflows API. The `status` in particular
contains the `phase` which can be "Succeeded", "Failed" etc, along with the `nodes` of the workflow.

Taking an example workflow definition that we can retrieve from a function such as:

```py
@script(outputs=Parameter(name="message-out", value_from={"path": "/tmp/message-out"}))
def echo_to_param(message: str):
    with open("/tmp/message-out", "w") as f:
        f.write(message)

def get_workflow_definition() -> Workflow:
    with Workflow(generate_name="hello-world-", entrypoint="steps") as w:
        with Steps(name="steps"):
            echo_to_param(arguments={"message": "Hello world!"})
    return w
```

We can write a test like so:

```py
def test_create_workflow():
    workflow = get_workflow_definition()
    model_workflow = workflow.create(wait=True)
    assert model_workflow.status and model_workflow.status.phase == "Succeeded"

    echo_node = next(
        filter(
            lambda n: n.display_name == "echo-to-param",  # use display_name to get the human-readable name of the nodes
            model_workflow.status.nodes.values(),
        )
    )

    message_out = next(filter(lambda n: n.name == "message-out", echo_node.outputs.parameters))
    assert message_out.value == "Hello world!"
```

Good luck, and happy Hera-ing!
