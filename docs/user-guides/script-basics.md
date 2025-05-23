# Script Basics

The `script` decorator is an essential part of Hera's extension on top of Argo.
[Script templates](https://argoproj.github.io/argo-workflows/fields/#scripttemplate) can run other scripting languages,
but in Hera, running Python becomes the standard.

## Script Decorator

The `script` decorator can turn any user-defined function into a template for Argo. Call the function under a Hera
context manager such as a `Workflow` or `Steps` context to create templates or an individual `Step`. The function will
still behave as normal outside of Hera contexts, meaning you can write unit tests on the given function.

When decorating a function, you should pass `Script` parameters to the `script` decorator. This includes values such as
the `image` to use, and `resources` to request.

```py
from hera.workflows import Resources, script

@script(image="python:3.11", resources=Resources(memory_request="5Gi"))
def echo(message: str):
    print(message)
```

When calling the function under a `Steps` or `DAG` context, you should pass `Step` or `Task` kwargs, such as the `name`
of the `Step`/`Task`, a `when` clause, `arguments` for the function, or a `with_param` list to loop over a given
template.

=== "Hera"

    ```py
    with Workflow(generate_name="dag-diamond-", entrypoint="diamond") as w:
        with DAG(name="diamond"):
            A = echo(name="A", arguments={"message": "A"})
            B = echo(name="B", arguments={"message": "B"}, when=f"{A.result} == 'A'")
            C = echo(name="C", arguments={"message": "C"}, when=f"{A.result} != 'A'")
            D = echo(name="D", arguments={"message": "D"})
            A >> [B, C] >> D
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dag-diamond-
    spec:
      entrypoint: diamond
      templates:
      - name: diamond
        dag:
          tasks:
          - name: A
            template: echo
            arguments:
              parameters:
              - name: message
                value: A
          - name: B
            depends: A
            template: echo
            when: '{{tasks.A.outputs.result}} == ''A'''
            arguments:
              parameters:
              - name: message
                value: B
          - name: C
            depends: A
            template: echo
            when: '{{tasks.A.outputs.result}} != ''A'''
            arguments:
              parameters:
              - name: message
                value: C
          - name: D
            depends: B && C
            template: echo
            arguments:
              parameters:
              - name: message
                value: D
      - name: echo
        inputs:
          parameters:
          - name: message
        script:
          image: python:3.12
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: message = json.loads(r'''{{inputs.parameters.message}}''')
            except: message = r'''{{inputs.parameters.message}}'''

            print(message)
          command:
          - python
    ```

<details><summary><i>How it works</i></summary>

The <code>script</code> decorator function prepares a <code>Script</code> object so that, when your function is invoked
under a Hera context, the call is redirected to the <code>Script.__call__</code> function. This takes the kwargs of a
<code>Step</code> or <code>Task</code> depending on whether the context manager is a <code>Steps</code> or a
<code>DAG</code>. Under a Workflow itself, your function is not expected to take arguments, so the call will add the
function as a template.

</details>

This acts as syntactic sugar for the alternative of using `Script` and `Task` directly to construct the Workflow and
DAG:

=== "Hera"

    ```py
    def echo(message):
        print(message)

    with Workflow(generate_name="dag-diamond-", entrypoint="diamond") as w:
        echo_template = Script(name="echo", source=echo, image="python:3.11", resources=Resources(memory_request="5Gi"))
        with DAG(name="diamond"):
            A = Task(name="A", template=echo_template, arguments={"message": "A"})
            B = Task(name="B", template=echo_template, arguments={"message": "B"}, when=f"{A.result} == 'A'")
            C = Task(name="C", template=echo_template, arguments={"message": "C"}, when=f"{A.result} != 'A'")
            D = Task(name="D", template=echo_template, arguments={"message": "D"})
            A >> [B, C] >> D
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dag-diamond-
    spec:
      entrypoint: diamond
      templates:
      - name: echo
        inputs:
          parameters:
          - name: message
        script:
          image: python:3.11
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: message = json.loads(r'''{{inputs.parameters.message}}''')
            except: message = r'''{{inputs.parameters.message}}'''

            print(message)
          command:
          - python
          resources:
            requests:
              memory: 5Gi
      - name: diamond
        dag:
          tasks:
          - name: A
            template: echo
            arguments:
              parameters:
              - name: message
                value: A
          - name: B
            depends: A
            template: echo
            when: '{{tasks.A.outputs.result}} == ''A'''
            arguments:
              parameters:
              - name: message
                value: B
          - name: C
            depends: A
            template: echo
            when: '{{tasks.A.outputs.result}} != ''A'''
            arguments:
              parameters:
              - name: message
                value: C
          - name: D
            depends: B && C
            template: echo
            arguments:
              parameters:
              - name: message
                value: D
    ```

## Script Constructors

Script constructors transform a script function into the template seen in YAML. Hera offers two built-in constructors
for you to use and extend.

### Inline Scripts

The `InlineScriptConstructor` is the default script constructor used to create "inline" scripts∑. It dumps the Python
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

#### Importing modules

A caveat of the `InlineScriptConstructor` is that it is quite limited - as the `InlineScriptConstructor` dumps your code
to the `source` field as-is, you must also `import` (within the function itself) any modules you use in the function:


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
Python image, specified by the `image` argument of the decorator. Therefore, if you use non-standard imports, such as
`numpy`, you will need to use an image that includes `numpy`, or build your own (e.g. as a Docker image).

### Runner Scripts

The `RunnerScriptConstructor` uses the "Hera Runner" to run your function on Argo. This avoids dumping the function to
the `source` of a template, keeping the YAML manageable and small, and allows you to arrange your code in natural Python
fashion:

* imports can be anywhere in the package
* the script-decorated function can call other functions in the package
* the function itself can take any serialisable class as inputs; it automatically handles basic types and Pydantic
  classes.

You'll need to build your own image to use a "runner" constructor, from the source code package itself and its
dependencies, including Hera itself to run the `hera.workflows.runner` module.

A script decorator can set its `constructor` to `"runner"` to use the built-in `RunnerScriptConstructor`, or use
`global_config.set_class_defaults(Script, constructor="runner")` to set it once for all script-decorated functions. You
should also set the `image` of the script in the same way.

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

From the YAML you will see we are running the `hera.workflows.runner` module. We pass the entrypoint argument via the
`-e` flag which is in `module:function` form, which is the `examples.workflows.callable_script` module containing
`my_function`.

You must build the image `my-code-image:v1` and it must be accessible from Argo **before** you submit the Workflow.

The `source` contains the input parameters, which are loaded and passed to the entrypoint. You will notice some
pecularities of this template.

> This is because in Argo, the value passed to `source` is dumped to a file, and then the filename is passed as the
> final argument to the `command`. Therefore, the `source` will actually contain a list of parameters as dictionaries,
> which are dumped to a file which is passed to `hera.workflows.runner`. Of course, this is all handled for you!

#### Integrated Pydantic Support

As Argo deals with a limited set of YAML objects (YAML is generally a superset of JSON), Pydantic support is practically
built-in to Hera through Pydantic's serialization to, and from, JSON. Using Pydantic objects (instead of dictionaries)
in Runner Script templates makes them less error-prone, and easier to write! Using Pydantic classes in function inputs
is as simple as inheriting from Pydantic's `BaseModel`.
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

Your functions can also return objects that are serialized, passed to another `Step` as a string argument, and then
de-serialized in another function. This flow can be seen in
[the callable scripts example](../examples/workflows/scripts/callable_script.md).

Read on to [Script Annotations](script-annotations.md) to learn how to write Script template functions even more
effectively!
