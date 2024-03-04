# Script Basics

The `Script` class is an essential part of Hera's extension on top of Argo. As Hera is a Python library,
[Script templates](https://argoproj.github.io/argo-workflows/fields/#scripttemplate) running Python become the standard
template, which is reflected by the greater feature set provided for writing them.

## Script Decorator

The `script` decorator function is a key offering of Hera to achieve near-native Python function orchestration. It
allows you to call the function under a Hera context manager such as a `Workflow` or `Steps` context, and it will be
treated as the intended sub-object, which would be a `template` when under a `Workflow`, or a `Step` when under a
`Steps`. The function will still behave as normal outside of any Hera contexts, meaning you can write unit tests on the
given function.

> **For advanced users**: the exact mechanism of the `script` decorator is to prepare a `Script` object within the
> decorator, so that when your function is invoked under a Hera context, the call is redirected to the `Script.__call__`
> function. This takes the kwargs of a `Step` or `Task` depending on whether the context manager is a `Steps` or a
> `DAG`. Under a Workflow itself, your function is not expected to take arguments, so the call will add the function as
> a template.

When decorating a function, you should pass `Script` parameters to the `script` decorator. This includes values such as
the `image` to use, and `resources` to request.

```py
from hera.workflows import Resources, script

@script(image="python:3.11", resources=Resources(memory_request="5Gi"))
def echo(message: str):
    print(message)
```

When calling the function under a `Steps` or `DAG` context, you should pass `Step` or `Task` kwargs, such as the `name`
of the `Step`/`Task`, a `when` clause, a `with_param` list to loop over a given template, or `arguments` for the
function.

```py
with Workflow(generate_name="dag-diamond-", entrypoint="diamond") as w:
    with DAG(name="diamond"):
        A = echo(name="A", arguments={"message": "A"})
        B = echo(name="B", arguments={"message": "B"}, when=f"{A.result == 'A'}")
        C = echo(name="C", arguments={"message": "C"}, when=f"{A.result != 'A'}")
        D = echo(name="D", arguments={"message": "D"})
        A >> [B, C] >> D
```

Alternatively, you can specify your DAG using `Task` directly:

```py
with Workflow(generate_name="dag-diamond-", entrypoint="diamond") as w:
    with DAG(name="diamond"):
        A = Task(name="A", source=echo, arguments={"message": "A"})
        B = Task(name="B", source=echo, arguments={"message": "B"}, when=f"{A.result == 'A'}")
        C = Task(name="C", source=echo, arguments={"message": "C"}, when=f"{A.result != 'A'}")
        D = Task(name="D", source=echo, arguments={"message": "D"})
        A >> [B, C] >> D
```

> **Note** in the `DAG` above, `D` will still run, even though `C` will be skipped. This is because of the `depends` logic
> resolving to `C.Succeeded || C.Skipped || C.Daemoned` due to Argo's default
> [depends logic](https://argoproj.github.io/argo-workflows/enhanced-depends-logic/#depends).

## Script Constructors

### InlineScriptConstructor

Script templates submitted to Argo typically run the given Python function in a Python image. By default, the Python
function itself is dumped to the YAML, and the Argo cluster will run that code. For the code below, we will see it
directly in the output YAML.

```py
from hera.workflows import Workflow, script

@script(add_cwd_to_sys_path=False)
def hello(s: str):
    print("Hello, {s}!".format(s=s))


with Workflow(
    generate_name="hello-world-",
    entrypoint="hello",
    arguments={"s": "world"},
) as w:
    hello()
```

We added `add_cwd_to_sys_path=False` to remove some boilerplate from the `source` below. You will see Hera adds a
`json.loads` to bridge the YAML input to a Python variable:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: hello-world-
spec:
  arguments:
    parameters:
    - name: s
      value: world
  entrypoint: hello
  templates:
  - inputs:
      parameters:
      - name: s
    name: hello
    script:
      command:
      - python
      image: python:3.8
      source: 'import json

        try: s = json.loads(r''''''{{inputs.parameters.s}}'''''')

        except: s = r''''''{{inputs.parameters.s}}''''''


        print(''Hello, {s}!''.format(s=s))'
```

This method of running the function is handled by the `InlineScriptConstructor`, called such because it constructs the
`Script` template to run the function "inline" in the YAML.

#### Importing modules

A caveat of the `InlineScriptConstructor` is that it is quite limited - as the `InlineScriptConstructor` dumps your code
to the `source` field as-is, you must also `import` (within the function itself) any modules you use in the function:

```py
@script(image="python:3.10")
def my_matcher(string: str):
    import re

    print(bool(re.match("test", string)))
```

> **Note** This also applies to other functions in your code - you will not be able to call functions defined outside of
> the scope of the script-decorated function!

If your function uses standard library imports from Python, you will be able to run your function with any standard
Python image, specified by the `image` argument of the decorator. Therefore, if you use non-standard imports, such as
`numpy`, you will need to use an image that includes `numpy`, or build your own (e.g. as a Docker image on DockerHub).

### RunnerScriptConstructor

The `RunnerScriptConstructor` is an alternative `ScriptConstructor` that uses the "Hera Runner" (think of this as being
like the PyTest Runner) to run your function on Argo. This avoids dumping the function to the `source` of a template,
keeping the YAML manageable and small, and allows you to arrange your code in natural Python fashion: imports can be
anywhere in the package, the script-decorated function can call other functions in the package, and the function itself
can take Pydantic objects as arguments. The use of the `RunnerScriptConstructor` necessitates building your own image,
as the Hera Runner runs the function by referencing it as an entrypoint of your module. The image used by the script
should be built from the source code package itself and its dependencies, so that the source code's functions,
dependencies, and Hera itself are available to run.

A function can set its `constructor` to `"runner"` to use the `RunnerScriptConstructor`, or use the
`global_config.set_class_defaults` function to set it once for all script-decorated functions. We can write a script
template function using Pydantic objects such as:

```py
global_config.set_class_defaults(Script, constructor="runner")

class Input(BaseModel):
    a: int
    b: str = "foo"

class Output(BaseModel):
    output: List[Input]

@script()
def my_function(input: Input) -> Output:
    return Output(output=[input])
```

This creates a template in YAML that looks like:

```yaml
- name: my-function
  inputs:
    parameters:
    - name: input
  script:
    command:
    - python
    args:
    - -m
    - hera.workflows.runner
    - -e
    - examples.workflows.callable_script:my_function
    image: my-image-with-python-source-code-and-dependencies
    source: '{{inputs.parameters}}'
```

You will notice some pecularities of this template. Firstly, it is running the `hera.workflows.runner` module, rather
than a user-module such as `examples.workflows.callable_script`. Instead, the `-e` arg specifies the `--entrypoint` to
be called by the runner, in this case the `my_function` of the `examples.workflows.callable_script` module. We do not
give a real `image` here, but we assume it exists in this example. Finally, the `source` parameter is passed the
`inputs.parameters` of the template. This is because the Hera Runner relies on a mechanism in Argo where the value
passed to `source` is dumped to a file, and then the filename is passed as the final `arg` to the `command`. Therefore,
the `source` will actually contain a list of parameters as dictionaries, which are dumped to a file which is passed to
`hera.workflows.runner`. Of course, this is all handled for you!
