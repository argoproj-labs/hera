# Parameters

In Argo Workflows, [Parameters](https://argoproj.github.io/argo-workflows/fields/#parameter) are used to specify inputs
and outputs of templates, as well as the arguments for template inputs when using the template. Hera aims to simplify
the use of Parameters through integrations with native functions.

## Default Values

Python functions allow default values in the function definition. When you decorate a function with Hera's `script`
decorator, any Python default values become default Parameter values for the template. For example, the Hera code below:

```py
@script()
def echo(message: str = "Hello world!"):
    print(message)
```

becomes:

```yaml
- name: echo
  inputs:
    parameters:
    - name: message
      default: Hello world!
  script:
    image: python:3.9
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

## Function Input Types

### Basic Usage for Inline Scripts

YAML accepts all the key basic types of JSON, including strings, numbers, bools, lists and dictionaries. For Inline
scripts, Hera interprets values passed into your function based on `json.loads`, *not the type you specify*, so the
example below will add `a` and `b` if the values passed in are interpreted as ints by `json.loads`, or concatenate them
if they are both strings:

=== "Hera"

    ```py
    @script()
    def add_values(a: int, b: str):
        print("Do we add or concatenate the values?")
        print(a + b)
    ```

=== "YAML"

    ```yaml
    - name: add-values
      inputs:
        parameters:
        - name: a
        - name: b
      script:
        image: python:3.9
        source: |-
          import os
          import sys
          sys.path.append(os.getcwd())
          import json
          try: a = json.loads(r'''{{inputs.parameters.a}}''')
          except: a = r'''{{inputs.parameters.a}}'''
          try: b = json.loads(r'''{{inputs.parameters.b}}''')
          except: b = r'''{{inputs.parameters.b}}'''

          print("Do we add or concatenate the values?")
          print(a + b)
        command:
        - python
    ```

> At runtime, `a` and `b` could be ints, or strings, or any other JSON types! Be careful relying on types in inline
> scripts!

### Enforcing Types Using the Hera Runner

To enforce types at runtime, you will need to build an image and use Hera's
[Script Runner](../user-guides/script-basics.md#runnerscriptconstructor). Then, the types will be validated at runtime
by Pydantic, and you can rely on the types being correct.

=== "Hera"

    ```py
    from hera.workflows import Steps, Workflow, script


    @script(constructor="runner", image="my-image:v1")
    def add_values(a: int, b: int):
        print("I know these are integers!")
        print(a + b)


    with Workflow(
        generate_name="validate-types-",
        entrypoint="steps",
    ) as w:
        with Steps(name="steps"):
            add_values(
                arguments={
                    "a": 1,
                    "b": 2,
                },
            )
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: validate-types-
    spec:
      entrypoint: steps
      templates:
      - name: steps
        steps:
        - - name: add-values
            template: add-values
            arguments:
              parameters:
              - name: a
                value: '1'
              - name: b
                value: '2'
      - name: add-values
        inputs:
          parameters:
          - name: a
          - name: b
        script:
          image: my-image:v1
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.misc.hello_world:add_values
          command:
          - python
    ```

### Custom Types

Hera uses Pydantic to allow any JSON-serialisable class to be used. You will need to build an image and use Hera's
[Script Runner](../user-guides/script-basics.md#runnerscriptconstructor). See an example usage
[here](../examples/workflows/scripts/callable_script.md).

## Output Parameters

### The `result` Output Parameter

The
[`result` output parameter](https://argoproj.github.io/argo-workflows/walk-through/output-parameters/#result-output-parameter)
captures the `stdout` of a template (that is, the `result` value is the *whole* stdout, including any log lines!) for
subsequent steps to use. In Hera, if we use a function under a `Steps` context, it returns a `Step` object, which has a
`result` property that we can access. For example, given the following functions:

```py
@script()
def hello(message: str):
    print(f"Hello {message}")

@script()
def repeat_back(message: str):
    print(f"You just said: '{message}'")
```

To get the stdout from running the `hello` Script template, we can assign the `Step` object returned from the function
call to a variable, and then we pass its `result` to the `repeat_back` template:

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

### Output Parameters for Inline Scripts

Normally in Argo Workflows, if you want an output parameter from a template, you will need to specify a file to export
the value from, and write to that file within the business logic of the template. Even in Hera, this can be quite
tedious and error-prone for inline scripts, with the `path` being in two separate places (or exposed as a global
variable):


=== "Hera"

    ```py
    from hera.workflows import Parameter, Steps, Workflow, script
    from hera.workflows.models import ValueFrom


    @script(
        outputs=[
            Parameter(name="hello-output", value_from=ValueFrom(path="/tmp/hello_world.txt")),
        ]
    )
    def hello_to_file():
        with open("/tmp/hello_world.txt", "w") as f:
            f.write("Hello World!")


    with Workflow(
        generate_name="hello-to-file-",
        entrypoint="steps",
        namespace="argo",
    ) as w:
        with Steps(name="steps"):
            hello_to_file(arguments={"message": "Hello world!"})
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: hello-to-file-
      namespace: argo
    spec:
      entrypoint: steps
      templates:
      - name: steps
        steps:
        - - name: hello-to-file
            template: hello-to-file
            arguments:
              parameters:
              - name: message
                value: Hello world!
      - name: hello-to-file
        outputs:
          parameters:
          - name: hello-output
            valueFrom:
              path: /tmp/hello_world.txt
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            with open('/tmp/hello_world.txt', 'w') as f:
                f.write('Hello World!')
          command:
          - python
    ```

The container logs for this `hello_to_file` step will show the artifact being exported as an output parameter.

```console
time="2023-05-26T11:16:37.907Z" level=info msg="/tmp/hello_world.txt -> /var/run/argo/outputs/parameters//tmp/hello_world.txt" argo=true
```

The output parameter will also show up in the UI under the node's INPUTS/OUTPUTS tab, similar to the table below.

| Parameters   |              |
| ------------ | ------------ |
| hello-output | Hello World! |

### Output Parameters for Runner Scripts

Output parameters are greatly simplified when using the Runner Scripts. You specify output parameters through the return
type annotation and return the value directly from the function (making testing much easier!), and the Hera runner will
handle the file saving for you:

```py
from typing import Annotated
from hera.workflows import Parameter, script

@script(constructor="runner", image="my-image:v1")
def hello() -> Annotated[str, Parameter(name="hello-output")]:
    return "Hello World!"
```

> Note: you will need to build an image from your code and dependencies to use the Hera Runner.

You can return multiple output parameters by using a `Tuple`:

```py
from typing import Annotated
from hera.workflows import Parameter, script

@script(constructor="runner", image="my-image:v1")
def hello() -> Tuple[
    Annotated[str, Parameter(name="hello-output-1")],
    Annotated[str, Parameter(name="hello-output-2")],
]:
    return "Hello World!", "Goodbye World!"
```

If you have many outputs, consider using [the Runner IO feature](../user-guides/script-runner-io.md) to avoid a
sprawling Tuple.

### Passing Output Parameters to Another Step

Under a `Steps` context, we can assign the `Step` object returned from the `hello_to_file` function, and use
`get_parameter`:

=== "Hera"

    ```py
    from hera.workflows import Parameter, Steps, Workflow, script
    from hera.workflows.models import ValueFrom


    @script(
        outputs=[
            Parameter(name="hello-output", value_from=ValueFrom(path="/tmp/hello_world.txt")),
        ]
    )
    def hello_to_file():
        with open("/tmp/hello_world.txt", "w") as f:
            f.write("Hello World!")


    @script()
    def repeat_back(message: str):
        print(f"You just said: '{message}'")


    with Workflow(
        generate_name="hello-world-parameter-passing-",
        entrypoint="steps",
    ) as w:
        with Steps(name="steps"):
            hello_world_step = hello_to_file()
            repeat_back(arguments={"message": hello_world_step.get_parameter("hello-output")})
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: hello-world-parameter-passing-
    spec:
      entrypoint: steps
      templates:
      - name: steps
        steps:
        - - name: hello-to-file
            template: hello-to-file
        - - name: repeat-back
            template: repeat-back
            arguments:
              parameters:
              - name: message
                value: '{{steps.hello-to-file.outputs.parameters.hello-output}}'
      - name: hello-to-file
        outputs:
          parameters:
          - name: hello-output
            valueFrom:
              path: /tmp/hello_world.txt
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            with open('/tmp/hello_world.txt', 'w') as f:
                f.write('Hello World!')
          command:
          - python
      - name: repeat-back
        inputs:
          parameters:
          - name: message
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: message = json.loads(r'''{{inputs.parameters.message}}''')
            except: message = r'''{{inputs.parameters.message}}'''

            print(f"You just said: '{message}'")
          command:
          - python
    ```

=== "Logs"

    ```console
    hello-world-parameter-passing-vq7pm-hello-to-file-3540104653: time="2023-05-26T12:12:13.803Z" level=info msg="sub-process exited" argo=true error="<nil>"
    hello-world-parameter-passing-vq7pm-hello-to-file-3540104653: time="2023-05-26T12:12:13.803Z" level=info msg="/tmp/hello_world.txt -> /var/run/argo/outputs/parameters//tmp/hello_world.txt" argo=true
    hello-world-parameter-passing-vq7pm-repeat-back-3418430710: You just said: 'Hello World!'
    hello-world-parameter-passing-vq7pm-repeat-back-3418430710: time="2023-05-26T12:12:24.106Z" level=info msg="sub-process exited" argo=true error="<nil>"
    ```
