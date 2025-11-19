# Script Templates

Hera offers two versions of the `script` decorator which transforms regular Python functions into Script templates for
Argo Workflows.

## Inline Script Templates

The example Workflow seen in [Hello World](./hello-world.md) showed the `source` field containing some boilerplate and
the function body itself. This is the default setting for Hera, called "inline" script templates. Here are the key
points to remember:

* They work the same as running a file directly through Python on your local command line, like `python hello_world.py`.
* They should only be used for basic use cases and trying out Hera.
* As the function is dumped directly in the `source` field, you **cannot use external functions or module-level
  imports**; they must instead be contained within the function body.
  
Here's an example using an inline script:

=== "Hera"

    ```py
    from hera.workflows import Steps, Workflow, WorkflowsService, script


    @script()
    def echo(message: str):
        import random

        print(message)
        print("I'm rolling a die:", random.randint(1, 6))


    with Workflow(
        generate_name="hello-world-",
        entrypoint="steps",
        namespace="argo",
        workflows_service=WorkflowsService(host="https://localhost:2746")
    ) as w:
        with Steps(name="steps"):
            echo(arguments={"message": "Hello world!"})
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: hello-world-
      namespace: argo
    spec:
      entrypoint: steps
      templates:
      - name: steps
        steps:
        - - name: echo
            template: echo
            arguments:
              parameters:
              - name: message
                value: Hello world!
      - name: echo
        inputs:
          parameters:
          - name: message
        script:
          image: python:3.10
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: message = json.loads(r'''{{inputs.parameters.message}}''')
            except: message = r'''{{inputs.parameters.message}}'''

            import random
            print(message)
            print("I'm rolling a die:", random.randint(1, 6))
          command:
          - python
    ```


To learn more about Inline Scripts, see the
[Script Constructors user guide](../user-guides/script-constructors.md#inline-scripts).

## Runner Script Templates

Hera offers a more powerful script template through the "Hera Runner", creating "runner script templates". This is where
the code is built into an OCI image, and Hera runs the module/entrypoint for you. Using the Hera Runner allows more
streamlined use of Parameters and Artifacts, which will be discussed next in the walkthrough.

We can adapt the example above to use the Hera Runner: we simply add the `constructor` and `image` fields to the
script decorator. We can now also move the `import random` out of the function:

```py
from hera.workflows import Workflow, script
import random


@script(constructor="runner", image="my-image:v1")
def echo(message: str = "Hello world!"):
    print(message)
    print("I'm rolling a die:", random.randint(1, 6))


with Workflow(
    generate_name="hello-world-",
    entrypoint="hello",
) as w:
    echo()
```

We would then need to build `my-image:v1` using a tool like Docker, and then we will be able to run this workflow on Argo.

The YAML for the Workflow shows the changes under `script` - the `args` field in particular shows we are running the
`hera.workflows.runner` module, and passing an entrypoint via `-e`. The `source` contains the input parameters, which
are loaded and passed to the entrypoint:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: hello-world-
spec:
  entrypoint: hello
  templates:
  - name: echo
    inputs:
      parameters:
      - name: message
        default: Hello world!
    script:
      image: my-image:v1
      command:
      - python
      args:
      - -m
      - hera.workflows.runner
      - -e
      - examples.workflows.misc.hello_world:echo
      source: '{{inputs.parameters}}'
```

Although this YAML definition looks odd, it works because the value of `source` is simply pasted into a file in the
container running through Argo, and the filename is then passed as the final argument to the `command` with its `args`.
The value of `{{inputs.parameters}}` is the list of parameters in JSON form. You can see how Hera loads it in
[the source code](https://github.com/argoproj-labs/hera/blob/86e25e/src/hera/workflows/_runner/util.py#L274-L295) of the
runner util functions.

To learn more about Runner Scripts, see the
[Script Constructors user guide](../user-guides/script-constructors.md#runner-scripts).
