# Script Constructors

## Inline Scripts

The `InlineScriptConstructor` is the default script constructor used to create "inline" scripts. It dumps the Python
function verbatim to YAML, with some pre-amble to set up the `sys.path` and `json.loads` the variables. Compare the Hera
form of the Workflow to the YAML:

=== "Hera"

    ```py
    from hera.workflows import InlineScriptConstructor

    @script(constructor=InlineScriptConstructor())
    def hello(s: str):
        print("Hello, {s}!".format(s=s))


    with Workflow(
        generate_name="hello-world-",
        entrypoint="hello",
        arguments={"s": "world"},
    ) as w:
        hello()
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: hello-world-
    spec:
      entrypoint: hello
      templates:
      - name: hello
        inputs:
          parameters:
          - name: s
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: s = json.loads(r'''{{inputs.parameters.s}}''')
            except: s = r'''{{inputs.parameters.s}}'''

            print('Hello, {s}!'.format(s=s))
          command:
          - python
      arguments:
        parameters:
        - name: s
          value: world
    ```

### Limitations of inline scripts

A caveat of the `InlineScriptConstructor` is that it is quite limited - as your code is dumped to the `source` field
as-is, there are multiple limitations, described below. These limitations are all solved by
[runner scripts](#runner-scripts).

#### Importing modules

You must `import` any modules you use in the function, within the function itself:

=== "Hera"

    ```py
    @script()
    def hello(s: str):
        print("Hello, {s}!".format(s=s))

    @script()
    def my_matcher(string: str):
        import re

        print(bool(re.match("test", string)))

    with Workflow(
        generate_name="hello-world-",
        entrypoint="hello",
        arguments={"string": "tester"},
    ) as w:
        my_matcher()
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: hello-world-
    spec:
      entrypoint: hello
      templates:
      - name: my-matcher
        inputs:
          parameters:
          - name: string
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: string = json.loads(r'''{{inputs.parameters.string}}''')
            except: string = r'''{{inputs.parameters.string}}'''

            import re
            print(bool(re.match('test', string)))
          command:
          - python
      arguments:
        parameters:
        - name: string
          value: tester
    ```

> **Note** This also applies to other functions in your code - you will not be able to call functions defined outside of
> the scope of the script-decorated function!

If your function uses standard library imports from Python, you will be able to run your function with any standard
Python image, specified by the `image` argument of the decorator. However, if you use third-party imports, such as
`numpy`, you will need to use an image that includes `numpy`, or build your own (e.g. as a Docker image).

#### Input types

Only JSON types are currently allowed for inline scripts inputs, including strings, numbers, booleans, lists and
dictionaries. Dictionaries offer the most flexibility for large inputs but will have no type validation. Also note that
the runtime type given by `json.loads` may not match the type specified on the function.

#### Output types

No output types are currently allowed in inline scripts (due to the plain `return` when the function body is dumped).
You must print to stdout to use the `result` parameter, or write to a file to create output parameters.

## Runner Scripts

The `RunnerScriptConstructor` uses the Hera Runner to run your function on Argo. This allows you to arrange your code in
usual Python fashion:

* imports can be anywhere in the package
* the script-decorated function can call other functions in the package
* the function itself can take any serialisable class as inputs; it automatically handles basic types and Pydantic
  classes.

### Setting Up

You'll need to build your own image to use a "runner" constructor, from the source code package itself and its
dependencies, including Hera itself to run the `hera.workflows.runner` module.

A script decorator can set its `constructor` to `"runner"` to use the built-in `RunnerScriptConstructor`, or use:

```py
from hera.shared import global_config

global_config.set_class_defaults(Script, constructor="runner")
```

to set it once for all script-decorated functions. You can also set the `image` for all scripts through `global_config`:

```py
global_config.image = "my-code-image:v1"
```

We can write a script template function using Pydantic objects such as:

=== "Hera"

    ```py
    from hera.workflows import RunnerScriptConstructor
    from pydantic.v1 import BaseModel

    class Input(BaseModel):
        a: int
        b: str = "foo"

    class Output(BaseModel):
        output: List[Input]

    @script(constructor=RunnerScriptConstructor(), image="my-code-image:v1")
    def my_function(input: Input) -> Output:
        return Output(output=[input])
        
    with Workflow(
        generate_name="hello-world-",
        entrypoint="hello",
        arguments={"input": Input(a=42)},
    ) as w:
        my_function()
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: hello-world-
    spec:
      entrypoint: hello
      templates:
      - name: my-function
        inputs:
          parameters:
          - name: input
        script:
          image: my-code-image:v1
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.callable_script:my_function
          command:
          - python
      arguments:
        parameters:
        - name: input
          value: '{"a": 42, "b": "foo"}'
    ```

The YAML shows we are running the `hera.workflows.runner` module. We pass the entrypoint argument via the `-e` flag
which is in `module:function` form, which is the `examples.workflows.callable_script` module containing `my_function`.

By not dumping the function to the `source` of a template, we can keep the YAML manageable and small for GitOps. The
`source` field actually contains the input parameters which are loaded from a file and passed to the `runner` when
running the template.

Note that you must build the image (in this case `my-code-image:v1`), and it must be accessible from Argo **before** you
submit the Workflow.

### Integrated Pydantic Support

[Pydantic](https://docs.pydantic.dev/latest/) can serialise to, and deserialise from, JSON, which allows Hera to easily
pass Pydantic objects between scripts. As a Workflow is a live object on Kubernetes, it must be able to represent all
its fields in YAML, so only string-serialisable values are possible.

Using Pydantic objects in Runner Script templates makes them less error-prone, and easier to write. Using Pydantic
classes in function inputs is as simple as inheriting from Pydantic's `BaseModel`.
[Read more about Pydantic models here](https://docs.pydantic.dev/latest/usage/models/).

```py
from pydantic import BaseModel
from hera.workflows import script

class MyModel(BaseModel):
    my_int: int
    my_string: str

@script(constructor="runner")
def my_pydantic_function(my_pydantic_input: MyModel):
    print(my_pydantic_input.my_string, my_pydantic_input.my_int)
```

Your functions can also return objects that are serialised, passed to another `Step`/`Task` as a string argument, and
then de-serialised in another function. This flow can be seen in
[the typed script IO example](../examples/workflows/hera-runner/typed_script_input_output.md).

If you need custom serialisation, read on to [Script Annotations](script-annotations.md) to learn more and how to write
script templates effectively!
