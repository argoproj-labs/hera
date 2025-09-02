# Decorators

Proposed in [HEP0001](https://github.com/argoproj-labs/hera/blob/73861b/proposals/heps/0001-decorators.md), decorators
for the other main template types were added in Hera v5.16. They can be used to write Workflows in a more familiar
Pythonic fashion, taking inspiration from projects such as FastAPI. This feature is intended to replace the context
manager syntax (but the context manager syntax will continue to be supported).

The decorators introduced in v5.16 are members of the `Workflow` class, meaning they can manipulate values within that
`Workflow`. The new decorators introduced are:

* `dag`
* `steps`
* `container`
* `script`
* `data`
* `http`
* `resource`
* `suspend_template`
* `set_entrypoint`

If you want to declare inputs and outputs in your templates, you must use the special `Input` and `Output` Pydantic
classes from `hera.workflows` so that Hera can deduce the inputs and outputs of your templates from the fields declared
in the classes.

You must also install the optional extras under `experimental` to enable the full feature set for decorators

```bash
pip install hera[experimental]
```

## `dag` and `steps`

The `dag` and `steps` decorator bring brand-new functionality to Hera, as they allow you to run and test your dag and
steps functions entirely locally. Note that as you are running pure Python code, features of Argo Workflows are not
supported when running locally, such as expressions. We plan on adding support for expressions so that conditional tasks
can be correctly skipped.

The `dag` decorator is also special in that it is able to automatically deduce the dependency relationships between
tasks. It does this by tracking the parameters and artifacts passed between tasks because the code within the function
must be written in a natural running order (which is also why it can be run locally). Note that only a basic "depends"
relationship is deduced, more complex dependencies are not yet supported.

The `steps` decorator allows you to use the `parallel` function from `hera.workflows`, which is used to open a context
under which all the steps will run in parallel.

The choice between `dag` and `steps` to arrange your templates mostly comes down to personal preference. If you want to
run as many _dependent_ templates in parallel as possible then use a DAG, which will figure out which tasks can run
first. If you want to run templates sequentially, and have more control over the running order and when to parallelise,
use `steps`.

## `container`

The `container` decorator is a convenient way to declare your container templates in Python, though the feature set is
limited. You can specify the `command` and `args` in the decorator arguments, and the inputs and outputs in the function
signature. You can leave the function as a stub or add some code to be able to run the function locally - consider it as
a "mockable" function.

## `script`

The new `script` decorator works the same as the old decorator in terms of declaring `script` attributes in the
decorator function. For the inputs and outputs of the function however, you now must use a subclass of the `Input` and
`Output`. This is the same behaviour as the experimental [Script Runner IO](./script-runner-io.md) for the old script
decorator.

Using this decorator will enforce usage of the `RunnerScriptConstructor`, so you must ensure you use an image built from
your code.

## `data`, `http`, `resource`, and `suspend_template`

These decorators allow you to define additional Argo Workflow template types in a Pythonic way. For more information on
how to use these templates, please refer to the relevant examples.

- [`data` decorator example](../examples/workflows/experimental/new_data_decorator.md)
- [`http` decorator example](../examples/workflows/experimental/new_http_decorator.md)
- [`resource` decorator example](../examples/workflows/experimental/new_resource_decorator.md)
- [`suspend_template` decorator example](../examples/workflows/experimental/new_suspend_decorator.md)

## `set_entrypoint`

The `set_entrypoint` decorator is a simple decorator with no arguments, used to set the `entrypoint` of the `Workflow` that you're declaring.

## Using decorators

Let's take a look at an example using scripts and steps.

```py
from hera.shared import global_config
from hera.workflows import Input, Output, WorkflowTemplate

global_config.experimental_features["decorator_syntax"] = True

w = WorkflowTemplate(name="my-template")

class MyInput(Input):
    user: str

class MyOutput(Output):
    my_str: str

@w.script()
def hello_world(my_input: MyInput) -> MyOutput:
    output = MyOutput()
    output.my_str = f"Hello Hera User: {my_input.user}!"
    return output

# You can pass script kwargs (including an alternative public template name) in the decorator
@w.script(name="goodbye-world", labels={"my-label": "my-value"})
def goodbye(my_input: MyInput) -> Output:
    output = Output()
    output.result = f"Goodbye Hera User: {my_input.user}!"
    return output


@w.set_entrypoint
@w.steps()
def my_steps() -> None:
    hello_world(MyInput(user="elliot"))
    goodbye(MyInput(user="elliot"))
```

For the line-by-line explanation, let's start with

```py
global_config.experimental_features["decorator_syntax"] = True
```

The new decorators are an experimental feature, so must be turned on via the `global_config`.

Then, in the world of decorators in Hera, we declare a `WorkflowTemplate` upfront, instead of using the `with WorkflowTemplate` syntax:

```py
w = WorkflowTemplate(name="my-template")
```

We need to use the decorators which are members of `Workflow`, as they link the given function as a template to the `Workflow`.

Then, we declare some Input/Output classes, inheriting from the Pydantic classes:

```py
class MyInput(Input):
    user: str

class MyOutput(Output):
    my_str: str
```

Here, we're setting up the `MyInput` class which will be converted to a set of template inputs; here, that only consists
of the `user` parameter, which is of type `str` - Hera will do the type checking for you when running with the
[Hera Runner](script-constructors.md#runner-scripts)!. We also have the template outputs contained in `MyOutput`. The `Output` class also contains the
`exit_code` and `result` fields, which are used by the Hera Runner to exit a script with the given exit code, and to
print a value to stdout to act as a step or task's
[special "result" output parameter](https://argo-workflows.readthedocs.io/en/stable/walk-through/output-parameters/#result-output-parameter).

Next, we declare two `script` templates:

```py
@w.script()
def hello_world(my_input: MyInput) -> MyOutput:
    output = MyOutput()
    output.my_str = f"Hello Hera User: {my_input.user}!"
    return output

# You can pass script kwargs (including an alternative public template name) in the decorator
@w.script(name="goodbye-world", labels={"my-label": "my-value"})
def goodbye(my_input: MyInput) -> Output:
    output = Output()
    output.result = f"Goodbye Hera User: {my_input.user}!"
    return output
```

Note that in `hello_world` we are using a `MyOutput` class, which means we can set the `my_str` output parameter, while
in `goodbye`, we are using the basic `Output` class, so we set the special `result` output parameter.

Then, we set up a `steps` template, setting it as the entrypoint, as follows:

```py
@w.set_entrypoint
@w.steps()
def my_steps() -> None:
    hello_world(MyInput(user="elliot"))
    goodbye(MyInput(user="elliot"))
```

We can simply call the script templates, passing the input objects in.


## Passing extra `kwargs`

In order to access normal `Step` and `Task` functionality, such as loops through `with_items`, you can pass extra kwargs
when calling the function in the steps or dag function.

!!! warning

    Running this particular `steps` function locally will not loop over the items in `with_items`. In general, the extra
    kwargs will not work with local-running `dag` and `steps` functions in the way you might expect, as there is no
    local-runtime for interpreting these values. Please see issue
    [#1492](https://github.com/argoproj-labs/hera/issues/1492) for updates on Hera's local runtime feature for
    decorators.

```py
w = Workflow(
    generate_name="fanout-workflow-",
)


class PrintMessageInput(Input):
    message: str


@w.script()
def print_message(inputs: PrintMessageInput):
    print(inputs.message)


@w.set_entrypoint
@w.steps()
def loop_example():
    print_message(
        PrintMessageInput(message="{{item}}"),
        name="print-message-loop-with-items",
        with_items=["hello world", "goodbye world"],
    )
```

!!! warning

    Your IDE/linter may complain about this function call, as it will not recognise the magic that Hera does at compile
    time. For that reason, until we can improve on this user experience and confirm it is the right way forward,
    decorators will remain experimental for the foreseeable future. Your input is appreciated in the
    [Hera Slack channel](https://cloud-native.slack.com/archives/C03NRMD9KPY) and
    [GitHub discussions](https://github.com/argoproj-labs/hera/discussions)!

For more examples, including use of a dag, see
[the "experimental" examples](../examples/workflows/experimental/new_dag_decorator_params.md).
