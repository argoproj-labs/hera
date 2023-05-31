# Parameters

In [Hello World](hello-world.md), a simple use of parameters was introduced, namely a Python function that takes
kwargs. We'll now explore how Hera exposes other features of Argo's
[Parameters](https://argoproj.github.io/argo-workflows/fields/#Parameter).

## Default Values

A Python function naturally allows default values in its definition. When you decorate a function with Hera's `script`
decorator, it lifts out the default value into a Parameter's `default`.

```py
@script()
def echo(message: str = "Hello world!"):
    print(message)
```

We can run this function in a workflow as defined below:

```py
with Workflow(
    generate_name="hello-world-",
    entrypoint="steps",
) as w:
    with Steps(name="steps"):
        echo()
```

And we'll see logs in Argo like

```console
hello-world-r96ww-echo-1258475821: Hello world!
```

## Types

Python functions don't just take strings, of course, and the key basic types YAML allows are strings, ints, bools and
dictionaries. Hera interprets values passed into your function via `json.loads`, so the below will add `a` and `b` if
the values passed in are interpreted as ints by `json.loads`.

```py
@script()
def add_values(a: int, b: int):
    print("Adding values")
    print(a + b)
```

i.e. the two calls to `add_values` below are equivalent as the strings in the second call are interpreted as integers.
Note that when reusing a function in multiple steps, you must give unique names to the `name` parameter.

```py
with Steps(name="steps"):
        add_values(name="first", arguments={"a": 1, "b": 2})
        add_values(name="second", arguments={"a": "1", "b": "2"})  # "1" and "2" will be treated as ints
```

<details>
<summary>See the logs from this run</summary>

Note the different node IDs (the number after `add-values`) in the logs, as the logs do not show the container names
"first" and "second".

```console
add-values-xw7k9-add-values-242584704: Adding values
add-values-xw7k9-add-values-242584704: 3
add-values-xw7k9-add-values-242584704: time="2023-05-26T11:57:13.805Z" level=info msg="sub-process exited" argo=true error="<nil>"
add-values-xw7k9-add-values-838832153: Adding values
add-values-xw7k9-add-values-838832153: 3
add-values-xw7k9-add-values-838832153: time="2023-05-26T11:57:24.101Z" level=info msg="sub-process exited" argo=true error="<nil>"
```
</details>

## Dictionaries

If we have a function that takes a dict such as below:

```py
@script()
def echo_a_dict(my_dict: Dict[str, str]):
    for k, v in my_dict.items():
        print(f"{k}={v}")
```

Then in the snippet below, during the compilation of the workflow, `arguments` will serialize the `dict` value of
`my_dict` via `json.dumps`. Then during the script execution on Argo, `json.loads` will load the `dict` and the function
will run as expected.

```py
with Workflow(
    generate_name="echo-dict-",
    entrypoint="steps",
) as w:
    with Steps(name="steps"):
        echo_a_dict(
            arguments={
                "my_dict": {
                    "my_key": "my_value",
                    "my_second_key": "my_second_value",
                }
            }
        )

w.create()
```

The logs for the workflow will show

```console
my_key=my_value
my_second_key=my_second_value
```

## Custom Types

Currently, custom types are only supported in the "script runner" experimental feature. See an example usage
[here](../../examples/workflows/callable_script.md). Please note this is an experimental feature so support is limited for now.

## Passing Parameters

### The `result` Output Parameter

For the previous examples, we've been printing output to stdout, which allows subsequent steps to access the value from
the
[`result` output parameter](https://argoproj.github.io/argo-workflows/walk-through/output-parameters/#result-output-parameter)
(that is, the `result` value *is* the stdout). In Hera, if we use a function under a `Steps` context, it returns a `Step`
object, which has a `result` property that we can access. For example, if we have the following functions:

```py
@script()
def hello(message: str):
    print(f"Hello {message}")

@script()
def repeat_back(message: str):
    print(f"You just said: '{message}'")
```

Let's say we want to get the stdout from running the `hello` Script template. We have to assign the `Step` object
returned from the function call to a variable, then we can access its `result` member, passing it to the `repeat_back`
template.

```py
with Workflow(
    generate_name="get-result-",
    entrypoint="steps",
) as w:
    with Steps(name="steps"):
        hello_step = hello(arguments={"message": "world!"})
        repeat_back(arguments={"message": hello_step.result})

w.create()
```

If you select "All" logs for the workflow you will see the stdout coming from each container:

```console
hello-world-ltpjt-hello-2151859747: Hello world!
hello-world-ltpjt-repeat-back-4012331575: You just said: 'Hello world!'
```


### Output Parameters

#### Creating Output Parameters

In general, output parameters are given values from a generated file rather than `stdout` like the `result` parameter.
You can do this in Hera by telling the script decorator to export the output from a file through a `value_from`. Ensure
you add the imports given below!

```py
from hera.workflows import Parameter, script
from hera.workflows.models import ValueFrom

@script(
    outputs=[
        Parameter(name="hello-output", value_from=ValueFrom(path="/tmp/hello_world.txt")),
    ]
)
def hello_to_file():
    with open("/tmp/hello_world.txt", "w") as f:
        f.write("Hello World!")
```

The container logs for this `hello_to_file` step will show the artifact being exported as an output parameter.

```console
time="2023-05-26T11:16:37.907Z" level=info msg="/tmp/hello_world.txt -> /var/run/argo/outputs/parameters//tmp/hello_world.txt" argo=true
```

The output parameter will also show up in the UI under the node's INPUTS/OUTPUTS tab, similar to the table below.

| Parameters   |              |
| ------------ | ------------ |
| hello-output | Hello World! |

#### Passing Output Parameters

Now that we have a `hello_to_file` function, let's use its output in our `repeat_back` function. Under a `Steps`
context, we can assign the `Step` object returned from the `hello_to_file` function, and use its `get_parameter`
function, and get the `Parameter`'s `value`.

```py
with Workflow(
    generate_name="hello-world-parameter-passing-",
    entrypoint="steps",
) as w:
    with Steps(name="steps"):
        hello_world_step = hello_to_file()
        repeat_back(
            arguments={"message": hello_world_step.get_parameter("hello-output").value}
        )
```

If you prefer, `arguments` can accept a single `Parameter`, and we can use the `with_name` function for convenience to
specify the right name for `repeat_back`:

```py
with Workflow(
    generate_name="hello-world-parameter-passing-",
    entrypoint="steps",
) as w:
    with Steps(name="steps"):
        hello_world_step = hello_to_file()
        repeat_back(
            arguments=hello_world_step.get_parameter("hello-output").with_name("message")
        )
```


Both of these Workflows will produce logs like

```console
hello-world-parameter-passing-vq7pm-hello-to-file-3540104653: time="2023-05-26T12:12:13.803Z" level=info msg="sub-process exited" argo=true error="<nil>"
hello-world-parameter-passing-vq7pm-hello-to-file-3540104653: time="2023-05-26T12:12:13.803Z" level=info msg="/tmp/hello_world.txt -> /var/run/argo/outputs/parameters//tmp/hello_world.txt" argo=true
hello-world-parameter-passing-vq7pm-repeat-back-3418430710: You just said: 'Hello World!'
hello-world-parameter-passing-vq7pm-repeat-back-3418430710: time="2023-05-26T12:12:24.106Z" level=info msg="sub-process exited" argo=true error="<nil>"
```
