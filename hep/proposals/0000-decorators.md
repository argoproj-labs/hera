# Meta
[meta]: #meta
- Name: Hera Decorator Syntax
- Start Date: 2024-04-13
- Author(s): [@samj1912](https://github.com/elliotgunton), [@elliotgunton](https://github.com/elliotgunton)
- Supersedes: (put "N/A" unless this replaces an existing HEP, then link to that HEP)

# Table of Contents
[table-of-contents]: #table-of-contents
- [Meta](#meta)
- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Motivation](#motivation)
- [Proposal](#proposal)
- [Code Examples](#code-examples)
  - [Basic Workflow](#basic-workflow)
  - [DAG Template](#dag-template)
  - [Steps Template](#steps-template)
  - [Container Template](#container-template)
  - [Workflow Template Ref](#workflow-template-ref)
  - [How to teach (OPTIONAL)](#how-to-teach-optional)
- [Implementation (OPTIONAL)](#implementation-optional)
  - [Link to the Implementation PR](#link-to-the-implementation-pr)
- [Migration (OPTIONAL)](#migration-optional)
- [Drawbacks](#drawbacks)
- [Alternatives](#alternatives)
- [Prior Art](#prior-art)
- [Unresolved Questions (OPTIONAL)](#unresolved-questions-optional)

# Overview
[overview]: #overview

This HEP introduces a new and powerful decorator based syntax for defining all kinds of Workflows and Templates.

# Motivation
[motivation]: #motivation

The current context manager based syntax is good but it doesn't map well to template types that contain inputs/outputs. With the `@script` decorator, we have made hera feel extremely Pythonic and it has the added benefit of being runnable locally. We wish to extend this syntax to other template types which will allow for better readability and local testing and it will also standardize the template interface for Argo Workflows.

# Proposal

This HEP proposes that every template be mapped into a decorated function with HeraIO classes as the inputs and outputs.

# Code Examples

## Basic Workflow

```python
from hera.workflows import WorkflowTemplate
from hera import io as hio

# We start by defining our Workflow Template
wt = WorkflowTemplate(name="my-template")

# This defines the a template input
class MyInput(hio.Input):
    user: str

@wt.entrypoint  # Sets hello_world as the default entrypoint for the workflow template
@wt.script  # Adds a new script template to the workflow template called hello_world
def hello_world(my_input: MyInput) -> hio.Output:
    output = hio.Output()
    output.result = f"Hello Hera User: {my_input.user}!"
    return output

# Allows users to instantiate a workflow template into a workflow
workflow = wt.run(MyInput(name="happy-hera-user"), wait=True)
# Returned workflow is a normal hera Workflow class and can be accessed as normal
assert workflow.status.phase == "Succeeded"
assert workflow.status.outputs.result == "Hello Hera User: happy-hera-user!"
```

## DAG Template

```python
from hera.workflows import WorkflowTemplate
from hera import io as hio
from hera.expr import spring

# We start by defining our Workflow Template
wt = WorkflowTemplate(name="my-template")

@wt.script  # Adds a new script template to the workflow template
def setup() -> hio.Output:
    return hio.Output(result="Setting things up")

class ConcatInput(hio.Input):
    word_a: str
    word_b: str

@wt.script  # Adds a new script template to the workflow template
def concat(concat_input: ConcatInput) -> hio.Output:
    return hio.Output(result=f"{concat_input.word_a} {concat_input.word_b}")

class WorkerInput(hio.Input):
    value_a: str
    value_b: str

class WorkerOutput(hio.Output):
    value: str


# The great outcome of this new syntax is that the template definition
# vs the template call becomes very explicit.
# When a template is defined, it is defined via the decorator which registers it
# When a template is invoked, it is invoked either via the callable syntax or via
# wt.run() if it is the entrypoint
# Another great side-effect is that all the templates can also be "run" locally as functions
@wt.entrypoint
@wt.dag
def worker(worker_input: WorkerInput) -> WorkerOutput:
    # We will need to use something like python-varname
    # to automatically create a task called "setup_task" here.
    setup_task = setup()
    # Note how easy it is to reference variables from the DAG template input
    # or previous tasks.
    task_a = concat(ConcatInput(word_a=worker_input.value_a, word_b=setup_task.result))
    task_b = concat(ConcatInput(word_a=worker_input.value_b, word_b=setup_task.result))
    final_task = concat(ConcatInput(word_a=task_a.result, word_b=task_b.result))
    # Note, we will automatically construct the dependency graph
    # based on the input/output relationship between tasks.
    # Users will still be able to explicitly add dependencies between tasks
    # using the rshift operator if they wish to define dependencies amongst
    # tasks that don't share variables directly
    return WorkerOutput(value=final_task.result)
```


## Steps Template

```python
from hera.workflows import WorkflowTemplate
from hera import io as hio

# We start by defining our Workflow Template
wt = WorkflowTemplate(name="my-template")

# This defines the a template input
class CalculatorInput(hio.Input):
    x: int
    y: int
    operation: Literal["add", "sub"] = "add"

@wt.script  # Adds a new script template to the workflow template called calculator
def calculator(calc_input: CalculatorInput) -> hio.Output:
    if calc_input.operation == "add":
        return hio.Output(calc_input.x + calc_input.y)
    return hio.Output(calc_input.x - calc_input.y)
    

# This defines the another template input
class FiboInput(hio.Input):
    num: int

class FiboOutput(hio.Output):
    num: int

@wt.entrypoint
@wt.steps  # Adds a new script template to the workflow template called fibonacci
def fibonacci(fibo: FiboInput) -> FiboOutput:
    # we will need to validate that users can only run/define certain kinds of expressions here
    # and throw warnings if they are using syntax that is invalid
    valid_number = hio.expr(fibo.num > 1)
    previous_num = calculator(CalculatorInput(x=fibo.num, y=1, operation="sub"), when=valid_number)
    previous_fibo = fibonacci(FiboInput(num=previous_num.result), when=valid_number)
    current = calculator(CalculatorInput(x=fibo.num, y=previous_fibo.num), when=valid_number)
    return FiboOutput(num=valid_number.check(current.num, 1))
```



## Container Template

```python
from hera.workflows import WorkflowTemplate, Container
from hera import io as hio

# We start by defining our Workflow Template
wt = WorkflowTemplate(name="my-template")

# This defines the a template input
class MyInput(hio.Input):
    user: str = "Hera"

class MyOutput(hio.Output):
    container_greeting: Annotated[str, Parameter(name="container-greeting")]

@wt.entrypoint
@wt.container(command=["sh", "-c"], args=["echo {{input.parameters.user}}"])
def basic_hello_world(my_input: MyInput) -> hio.Output:
    ...


@wt.entrypoint
@wt.container(command=["sh", "-c"])
def advanced_hello_world(my_input: MyInput, template: Container) -> MyOutput:
    # hio.output serves two functions. One, it allows users to create the output class
    # which allows output path variables to be referenced.
    # Second, it can be used to "mock" a container template when running locally and allow us to
    # inject outputs based on inputs.
    output: MyOutput = hio.output(my_input)
    # template is a special variable that allows you to reference the template itself and modify
    # its attributes. This is especially useful when trying to reference input params in args
    template.args = [f"echo {hio.name(my_input.user)} > {hio.path(output.container_greeting)}"]
    return output
```

## Workflow Template Ref

```python
from hera.workflows import WorkflowTemplate
from hera import io as hio
from hera.expr import spring

# We start by defining our Workflow Template
wt = WorkflowTemplate(name="my-template")

ewt = WorkflowTemplate(name="externally-workflow-template")
awt = WorkflowTemplate(name="another-workflow-template")

@awt.script  # Adds a new script template to a workflow template called "another-workflow-template"
def setup() -> hio.Output:
    return hio.Output(result="Setting things up")

class ConcatInput(hio.Input):
    word_a: str
    word_b: str


class ConcatOutput(hio.Output):
    value: str

# Adds a new template ref from an external template
# This can be auto-generated or typed by the user
@ewt.template_ref
def concat(concat_input: ConcatInput) -> ConcatOutput:
    ...
    # Note: we can optionally use hio.output(concat_input)
    # again here to run "local" mock versions of this workflow template ref
    # this will be useful in local testing

class WorkerInput(hio.Input):
    value_a: str
    value_b: str

class WorkerOutput(hio.Output):
    value: str


@wt.entrypoint
@wt.dag
def worker(worker_input: WorkerInput) -> WorkerOutput:
    # Note that here setup will be referenced as a workflow template ref
    # since it belongs in a different workflow template even though it is defined
    # inside this file
    setup_task = setup()
    # concat is a workflow template ref and just serves as a stub
    task_a = concat(ConcatInput(word_a=worker_input.value_a, word_b=setup_task.result))
    task_b = concat(ConcatInput(word_a=worker_input.value_b, word_b=setup_task.result))
    final_task = concat(ConcatInput(word_a=task_a.value, word_b=task_b.value))
    return WorkerOutput(value=final_task.value)
```



## How to teach (OPTIONAL)

If applicable, describe the differences between teaching this to existing users and new users.


# Implementation (OPTIONAL)

TODO: Add links about https://github.com/alexmojaki/sorcery#select_from, https://github.com/alexmojaki/executing#libraries-that-use-this and https://github.com/pwwang/python-varname

## Link to the Implementation PR

# Migration (OPTIONAL)

This section should document breaks to public API and breaks in compatibility due to this HEP's proposed changes. In addition, it should document the proposed steps that one would need to take to work through these changes.

# Drawbacks

Why should we **not** do this?

# Alternatives

- What other designs have been considered?
- Why is this proposal the best?
- What is the impact of not doing this?

# Prior Art

Discuss prior art, both the good and bad.

# Unresolved Questions (OPTIONAL)

- What parts of the design do you expect to be resolved before this gets merged?
- What parts of the design do you expect to be resolved through implementation of the feature?
- What related issues do you consider out of scope for this HEP that could be addressed in the future independently of the solution that comes out of this HEP?
