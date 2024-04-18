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
  - [Template Refs](#template-refs)
  - [Template Sets](#template-sets)
  - [How to teach](#how-to-teach)
- [Implementation](#implementation)
<!-- - [Migration (OPTIONAL)](#migration-optional) -->
- [Drawbacks](#drawbacks)
- [Alternatives](#alternatives)
- [Prior Art](#prior-art)
- [Unresolved Questions](#unresolved-questions)

# Overview
[overview]: #overview

This HEP introduces new and powerful decorator based syntax elements for defining Workflows and Templates.

# Motivation
[motivation]: #motivation

The current context manager based syntax is good (especially for bridging the gap from Python to Argo's YAML) but it doesn't map well to non-script template types that contain inputs/outputs like DAGs and Steps. It is also difficult for users to pass Parameters and Artifacts between Tasks and Steps.

With the `@script` decorator, we made Hera feel extremely Pythonic and it has the added benefit of being runnable locally. We wish to extend this syntax to other template types, namely DAGs, Steps and Containers, (and eventually other template types) which will allow for better readability and local testing. In this HEP, we also show how we will be able to generate stubs for WorkflowTemplates and improvements for referencing TemplateRefs under the new decorator syntax.

To outline the benefits of this proposal:
* DAGs and Steps made up of local script-decorated functions will be entirely locally runnable
  * We intend to follow up this HEP with a "locally-runnable expressions" HEP, to allow full conditional logic control in DAGs and Steps
* Parameter passing within DAGs and Steps will be simplified and read as Python-native code
* All templates will be mockable with user-defined snippets of Python code to allow you to locally test DAGs and Steps, so users will have the ability to specify the mocked outputs of a template
* You will be able to more easily arrange code for multiple WorkflowTemplates in one package as templates are tied to their respective WorkflowTemplates through the decorator
  * Tying templates to their respective WorkflowTemplates means we know that, when used in a DAG/Steps function, the function call to another WorkflowTemplate's template to create a Task/Step should be a `TemplateRef`
* You will be able to stub out templates from WorkflowTemplates, allowing you to use them in DAGs/Steps with full type information
  * We intend to follow up this HEP with a "stub generation" enhancement to the CLI, where these stubs will be generated via `hera generate stubs`

# Proposal

This HEP proposes that Argo's DAG, Steps and Container templates be mapped into Hera as decorated functions with HeraIO classes as the inputs and outputs. We will also introduce a new script decorator under the `hera.workflows.workflow.Workflow` class which will enforce use of the script runner along with the HeraIO classes.

> ⚠️ The existing context manager syntax, and the current script decorator, will continue to be supported, but they are
> unlikely to receive any active development of new features.

To allow Workflow definitions to span multiple files, we will also introduce a `TemplateSet` class offering the same decorators. This can then be used to collect templates (DAGs, scripts etc) in files `A.py` and `B.py`, while the `Workflow` object is defined in file `C.py`, which will import the `TemplateSet` from `A` and `B`, and will add all of those templates to the Workflow via a `w.add_template_set` function. This is analogous to [FastAPI's `include_router` mechanism](https://fastapi.tiangolo.com/reference/apirouter/?h=include_router#fastapi.APIRouter.include_router):

```py
from fastapi import APIRouter, FastAPI

app = FastAPI()
internal_router = APIRouter()
users_router = APIRouter()

@users_router.get("/users/")
def read_users():
    return [{"name": "Rick"}, {"name": "Morty"}]

internal_router.include_router(users_router)
app.include_router(internal_router)
```

# Code Examples

## Basic Workflow

```python
from hera.workflows import WorkflowTemplate
import hera.workflows.io as hio

# We start by defining our Workflow Template
wt = WorkflowTemplate(name="my-template")

# Users must subclass `hio.Input` to define the template's inputs
class MyInput(hio.Input):
    user: str

@wt.entrypoint  # Sets hello_world as the default entrypoint for the workflow template, it is an error to set entrypoint on multiple functions
@wt.script  # Adds a new script template to the workflow template called hello_world. This will enforce use of the script runner.
def hello_world(my_input: MyInput) -> hio.Output:  # A subclass of hio.Output must be used for the output of the function
    output = hio.Output()
    output.result = f"Hello Hera User: {my_input.user}!"
    return output

# `run` is a new function for users to instantiate a workflow template as a workflow
workflow = wt.run(MyInput(name="happy-hera-user"), wait=True)

# Returned workflow is a normal hera Workflow class and can be accessed as normal
assert workflow.status.phase == "Succeeded"
assert workflow.status.outputs.result == "Hello Hera User: happy-hera-user!"
```

## DAG Template

```python
from hera.workflows import WorkflowTemplate
import hera.workflows.io as hio

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


# The great outcome of this new syntax is is the separation of concerns so that
# the template definition vs the template call becomes very explicit.
# When a template is defined, it is defined via the decorator which registers it
# When a template is invoked, it is invoked either via the callable syntax or via
# wt.run() if it is the entrypoint
# Another great side-effect is that all the templates can run locally as functions
@wt.entrypoint
@wt.dag
def worker(worker_input: WorkerInput) -> WorkerOutput:
    # We will need to use something like python-varname
    # to automatically create a task called "setup_task" here.
    setup_task = setup()
    # setup_task will be a `Task` when building the workflow, vs an `hio.Output` object
    # when running locally.


    # Note how easy it is to reference variables from the DAG template input
    # or previous tasks.
    task_a = concat(ConcatInput(word_a=worker_input.value_a, word_b=setup_task.result))
    task_b = concat(ConcatInput(word_a=worker_input.value_b, word_b=setup_task.result))
    final_task = concat(ConcatInput(word_a=task_a.result, word_b=task_b.result))

    # Note, we will automatically construct the dependency graph based on the
    # input/output relationship between tasks, so Hera will infer the DAG as:
    # setup_task >> [task_a, task_b] >> final_task

    # Users will still be able to explicitly add dependencies between tasks
    # using the rshift operator if they wish to define dependencies amongst
    # tasks that don't share variables directly

    # Easily "forward" task output parameters to the DAG's output parameters
    # which replaces the existing syntax, which requires a "forward declaration"
    # of the intended output parameter:
    # with DAG(
    #     ...,
    #     outputs=Parameter(
    #         name="my-dag-output",
    #         value_from={"parameter": "{{task-name.outputs.parameters.param-name}}"},
    #     ),
    return WorkerOutput(value=final_task.result)
```

## Steps Template

```python
from hera.workflows import WorkflowTemplate
import hera.workflows.io as hio

# We start by defining our Workflow Template
wt = WorkflowTemplate(name="my-template")

# This defines the template's inputs
class CalculatorInput(hio.Input):
    x: int
    y: int
    operation: Literal["add", "sub"] = "add"

@wt.script  # Adds a new script template to the workflow template called calculator
def calculator(calc_input: CalculatorInput) -> hio.Output:
    if calc_input.operation == "add":
        return hio.Output(calc_input.x + calc_input.y)
    return hio.Output(calc_input.x - calc_input.y)
    

# This defines another template's inputs
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

### Parallel steps

Converting the DAG code:

```py
from hera.workflows import WorkflowTemplate, parallel
import hera.workflows.io as hio

# We start by defining our Workflow Template
wt = WorkflowTemplate(name="my-template")

@wt.script  # Adds a new script template to the workflow template
def setup() -> hio.Output:
    return hio.Output(result="success")

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


@wt.entrypoint
@wt.steps
def worker(worker_input: WorkerInput) -> WorkerOutput:
    setup_step = setup()

    # We can potentially add parameters such as `when` to `parallel` to add
    # the `when` clause to all sub-steps
    with parallel():
        step_a = concat(ConcatInput(word_a=worker_input.value_a, word_b=setup_step.result))
        step_b = concat(ConcatInput(word_a=worker_input.value_b, word_b=setup_step.result))

    final_step = concat(ConcatInput(word_a=step_a.result, word_b=step_b.result))
    return WorkerOutput(value=final_step.result)
```

## Container Template

```python
from hera.workflows import WorkflowTemplate, Container
import hera.workflows.io as hio

# We start by defining our Workflow Template
wt = WorkflowTemplate(name="my-template")

# This defines the template's inputs
class MyInput(hio.Input):
    user: str = "Hera"

class MyOutput(hio.Output):
    container_greeting: Annotated[
        str,
        Parameter(
            name="container-greeting",
            value_from={"path": "/tmp/hello_world.txt"},
        ),
    ]

@wt.entrypoint
@wt.container(command=["sh", "-c"], args=["echo Hello {{inputs.parameters.user}} | tee /tmp/hello_world.txt"])
def basic_hello_world(my_input: MyInput) -> hio.Output:
    ...


@wt.entrypoint
@wt.container(command=["sh", "-c"])
def advanced_hello_world(my_input: MyInput, template: Container) -> MyOutput:
    # A 'MyOutput' object can be used to "mock" the output when running locally and allow us to
    # inject outputs based on inputs.
    output: MyOutput = MyOutput(container_greeting=f"Hello {my_input.user}")

    # template is a special variable that allows you to reference the template itself and modify
    # its attributes. This is especially useful when trying to reference input params in args.
    # The hio.name and hio.path functions will be able to inspect the annotation of the given variable
    # to return the correct Argo template syntax substitution.
    template.args = [f"echo Hello {hio.name(my_input.user)} > {hio.path(output.container_greeting)}"]
    return output
```

## Template Refs

```python
from hera.workflows import WorkflowTemplate, ClusterWorkflowTemplate
import hera.workflows.io as hio

# We start by defining our Workflow Template
wt = WorkflowTemplate(name="my-template")

# We will be referring to "another-workflow-template", to demonstrate two WorkflowTemplates can be written in the same package
awt = WorkflowTemplate(name="another-workflow-template")

# We assume we can generate Python code for this (Cluster) Workflow Template from e.g `hera generate stubs external-workflow-template`.
# Ultimately, awt and ewt will behave the same way when their templates are invoked in dag/steps functions.
ewt = ClusterWorkflowTemplate(name="external-workflow-template")

@awt.script  # Adds a new script template to a workflow template called "another-workflow-template"
def setup() -> hio.Output:
    return hio.Output(result="Setting things up")

class ConcatInput(hio.Input):
    word_a: str
    word_b: str

class ConcatOutput(hio.Output):
    value: str

# We assume we can autogenerate stubs such as these for templates in "external-workflow-template"
@ewt.script
def concat(concat_input: ConcatInput) -> ConcatOutput:
    ...
    # Note: we can optionally return hio.output(concat_input)
    # again here to run "local" mock versions of this template ref
    # this will be useful in local testing

# In the case of kebab-case template names or other details, we can pass the extra info to the decorator:
@ewt.script(name="my-concat-function")
def my_concat_function(concat_input: ConcatInput) -> ConcatOutput:
    ...


class WorkerInput(hio.Input):
    value_a: str
    value_b: str

class WorkerOutput(hio.Output):
    value: str


@wt.entrypoint
@wt.dag
def worker(worker_input: WorkerInput) -> WorkerOutput:
    # Here, the call to `setup` will create a template ref task since it belongs
    # in a different workflow template even though it is defined inside this file
    setup_task = setup()

    # concat serves as a stub, and will also become a template ref task
    task_a = concat(ConcatInput(word_a=worker_input.value_a, word_b=setup_task.result))
    task_b = concat(ConcatInput(word_a=worker_input.value_b, word_b=setup_task.result))
    final_task = concat(ConcatInput(word_a=task_a.value, word_b=task_b.value))
    return WorkerOutput(value=final_task.value)
```

## Template Sets

```py
from hera.workflows import TemplateSet, WorkflowTemplate

wt = WorkflowTemplate(name="my-template")
templates = TemplateSet()

@templates.script
def setup() -> hio.Output:
    return hio.Output(result="Setting things up")

wt.add_template_set(templates)
```

## How to teach

Given the existing `script` decorator is used throughout the walk through and examples, we will need to be clear if and when we replace it with the workflow-specific `script` decorator, as the feature will need to go through the `experimental_features` route. We should then consider re-writing the walkthrough and key examples to use the new decorators. We may want to consider a migration guide or tool to convert from the old `script` to the new to make this easier for ourselves and our users.

# Implementation

The decorators for DAG, Steps and Containers, and the new Script decorator will be implemented as functions under the `hera.workflows.workflow.Workflow` class, in a similar fashion to the existing `script` decorator:

```py
class Workflow(
    ArgumentsMixin,
    ContextMixin,
    HookMixin,
    VolumeMixin,
    MetricsMixin,
    ModelMapperMixin,
):
    # ...

    def container(**container_kwargs) -> Callable:
        ...

    def dag(**dag_kwargs) -> Callable:
        ...

    def steps(**steps_kwargs) -> Callable:
        ...

    def script(**script_kwargs) -> Callable:
        ...
```

We will enforce the single input and output of the function within the decorator to be the `hera.workflows.io.Input` and `hera.workflows.io.Output` classes. We will repurpose the RunnerInput/RunnerOutput classes and deprecate the `script_pydantic_io` experimental feature, as we will stop development on the old `script` decorator to instead promote the new decorators as "the golden path" for development with Hera.

We require the use of special classes for the input/output of the function to allow a mechanism to switch between "build" code for when building a Workflow, versus local "running" code. Using a custom class means we can implement dunder methods like `__getattribute__` to intercept the call so that for a statement within a DAG/Steps function like from the DAG example:

```py
    task_a = concat(ConcatInput(word_a=worker_input.value_a, word_b=setup_task.result))
```

For the `worker_input.value_a` access, we can dynamically get the actual value when running locally, or create an argument `word_a` with the value `inputs.parameters.value_a` when building the workflow, i.e. for this `DAGTask` we will get the following YAML:

```yaml
- name: task_a
  template: concat
  arguments:
    parameters:
    - name: word_a
      value: {{inputs.parameters.value_a}}
    - name: word_b
      value: {{tasks.setup_task.outputs.result}}
```

Without the IO classes the building of the workflow would be more complicated as we would need to go through positional args to match them, but we then have the problem of wanting to allow `TemplateInvocatorSubNodeMixin` (Task/Step) kwargs without them clashing. By limiting functions to a single input and output, we can encapsulate the runtime/build time behaviour difference, as well as allowing Task/Step kwargs to be set as kwarg-only parameters to the function call.

Deeper in the backend, to be able to extract the names of tasks from statements like

```py
    task_a = concat(ConcatInput(word_a=worker_input.value_a, word_b=setup_task.result))
```

we need to make use of libraries that can perform AST inspection. `sorcery` introduces the ability to get the name of the variable itself through the `assigned_names` [function](https://github.com/alexmojaki/sorcery?tab=readme-ov-file#assigned_names). A library that builds off this is [python-varname](https://github.com/pwwang/python-varname), which is able to retrieve the name of the variable being assigned to by a function, from _inside_ the function:

```py
from varname import varname
def function():
    return varname()

func = function()  # func == 'func'
```

Therefore, in the new `script` decorator function, when building the workflow, we will need to use `varname` to get the Task or Step's name, which might look something like:

```py
class Workflow(...):

    def script(self, *args, **kwargs):
        def wrapper(f):
            signature = inspect.signature(f)
            outputs = signature.return_annotation
            inputs = signature.parameters['in_'].annotation
            s = Script(name=f.__name__)
            self._templates.append(s)
            def wrapped(*args, **kwargs):
                if building:
                    # name of the task/step, which may be in the kwargs or inferred from the variable name:
                    name = kwargs.pop("name", varname())
                    # ... implementation ...
```

# Drawbacks

* The existing syntax using context managers does a good job of mirroring the underlying YAML syntax of Argo Workflows, but can be confusing to regular Python users.
* By adding this feature, we are introducing another way of writing templates - we will need to ensure documentation is clear, and examples are updated to show which method they are using.
* We are unlikely to continue feature development on the current method of writing script templates.
  * We will be deprecating and removing the `script_pydantic_io` experimental feature, in favour of this HEP
  * We may also want to consider whether to graduate or deprecate the `script_annotations` experimental feature. It is a convenient way to write script templates with named Parameters using the current script decorator, but can harm readability, and the `tuple` type for outputs especially poses a problem for readability, so may be better to remove the `tuple` output and otherwise graduate that feature.

# Alternatives

We could keep only the current context manager syntax, however, users still struggle with passing parameters and have to resort to Argo's underlying esoteric YAML syntax, and DAG and Steps templates are not locally executable. Within the existing codebase/design of Hera, alternatives such as new classes don't make the most sense compared to decorators, as we have already set a precedent with the current `script` decorator.

# Prior Art

Comparisons to Prefect, Airflow and Metaflow, in particular in the context of parameter-passing between tasks.

## Prefect

As Prefect is in control of its own platform, it offers decorators for "flows" (equivalent to Argo's Workflows) and "tasks" (equivalent to DAGTasks) that do more of the behind the scenes magic for you, letting you use native Python code. Comparing to Hera, which must be able to compile the WorkflowTemplate definitions into YAML, we cannot lift _all_ of the backend implementation details into decorators in the same way.

```py
from prefect import flow, task

@task
def my_task():
    return 1

@flow
def my_flow():
    task_result = my_task()
    return task_result + 1

result = my_flow()
assert result == 2
```

Prefect exposes the concept of serializing - https://docs.prefect.io/latest/concepts/results/#result-serializer-types - and “types” of results https://docs.prefect.io/latest/concepts/results/#result-types - of which the “LiteralType” must be JSON serializable (similar to Hera’s Pydantic integration).

https://docs.prefect.io/latest/concepts/results/#retrieving-results

## Airflow

Airflow 1.0 used the concept of XCOMs to communicate between the isolated Task instances.

The new Airflow 2.0 library uses TaskFlows, similar to Prefect, letting you use native Python code.

```py
import json

import pendulum

from airflow.decorators import dag, task
@dag(
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["example"],
)
def tutorial_taskflow_api():
    """
    ### TaskFlow API Tutorial Documentation
    This is a simple data pipeline example which demonstrates the use of
    the TaskFlow API using three simple tasks for Extract, Transform, and Load.
    Documentation that goes along with the Airflow TaskFlow API tutorial is
    located
    [here](https://airflow.apache.org/docs/apache-airflow/stable/tutorial_taskflow_api.html)
    """
    @task()
    def extract():
        """
        #### Extract task
        A simple Extract task to get data ready for the rest of the data
        pipeline. In this case, getting data is simulated by reading from a
        hardcoded JSON string.
        """
        data_string = '{"1001": 301.27, "1002": 433.21, "1003": 502.22}'

        order_data_dict = json.loads(data_string)
        return order_data_dict

    @task(multiple_outputs=True)
    def transform(order_data_dict: dict):
        """
        #### Transform task
        A simple Transform task which takes in the collection of order data and
        computes the total order value.
        """
        total_order_value = 0

        for value in order_data_dict.values():
            total_order_value += value

        return {"total_order_value": total_order_value}
    @task()
    def load(total_order_value: float):
        """
        #### Load task
        A simple Load task which takes in the result of the Transform task and
        instead of saving it to end user review, just prints it out.
        """

        print(f"Total order value is: {total_order_value:.2f}")

    order_data = extract()
    order_summary = transform(order_data)
    load(order_summary["total_order_value"])

tutorial_taskflow_api()
```

Note that Airflow has abstracted away the construction of the DAG by using the outputs passed between tasks to derive the dependencies. This is new in Airflow 2.0. Previously, the `>>` syntax would be used.

These libraries don’t seem to have a concept of multiple outputs (despite the naming of `multiple_outputs` seen above - it simply means it's a dict), therefore it’s hard to compare that aspect. But for results, Hera already implements the `.result` property, which can be used in an equivalent way, even with the script runner, however, use of the script runner encourages explicit parameter outputs, to avoid using stdout to pass values.

## Metaflow

Metaflow is more of an experimentation/development platform, rather than being explicitly a Workflow Orchestrator with all the scaling, retry capabilities etc of something like Argo Workflows. "Steps" act as "checkpoints" for your code. The other main value-add of Metaflow is how it acts as the plumbing between different platforms, and allows local and remote execution of the same code, meaning it is suitable for the initial experimentation phase of the Model Development Lifecycle (MDLC). It appears to be less suitable to the later maintenance phase of the MDLC, as the rough code used for experimentation is less likely to be well-tested, compared to Hera, which lends itself to a full test suite of your code and Workflows through the use of the Script functions.

Something like a "[linear flow](https://docs.metaflow.org/metaflow/basics#linear)" in Metaflow is immediately understandable:
```py
from metaflow import FlowSpec, step

class LinearFlow(FlowSpec):

    @step
    def start(self):
        self.my_var = 'hello world'
        self.next(self.a)

    @step
    def a(self):
        print('the data artifact is: %s' % self.my_var)
        self.next(self.end)

    @step
    def end(self):
        print('the data artifact is still: %s' % self.my_var)

if __name__ == '__main__':
    LinearFlow()
```

Metaflow also has the problem of fan-out syntax being less native using "[foreach](https://docs.metaflow.org/metaflow/basics#foreach)":

```py
from metaflow import FlowSpec, step

class ForeachFlow(FlowSpec):

    @step
    def start(self):
        self.titles = ['Stranger Things',
                       'House of Cards',
                       'Narcos']
        self.next(self.a, foreach='titles')

    @step
    def a(self):
        self.title = '%s processed' % self.input
        self.next(self.join)

    @step
    def join(self, inputs):
        self.results = [input.title for input in inputs]
        self.next(self.end)

    @step
    def end(self):
        print('\n'.join(self.results))

if __name__ == '__main__':
    ForeachFlow()
```

# Unresolved Questions

This feature is independent of any current proposals, so once approved, this HEP can be implemented as written in the current code base.

Future features that are out of scope but will build off this HEP include
* the generation of stubs, which we have suggested will be through `hera generate stub`
* local expr evaluation, which has not been investigated in this HEP, but can be seen in example code proposed as `valid_number = hio.expr(fibo.num > 1)`
* the remaining template types like HTTP, resource etc which have not been investigated in this HEP
