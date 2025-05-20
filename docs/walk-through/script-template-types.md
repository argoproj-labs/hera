# Types of Script Templates

## Inline Script Templates

The example Workflows seen so far have shown the `source` field containing some boilerplate and the function body
itself. This is the default setting for Hera, called "inline" script templates. They work the same as running a file
directly through Python on your local command line, like `python hello_world.py`. They should only be used for basic use
cases and trying out Hera. As the function is dumped directly in the `source` field, you cannot use external functions
and imports, which must instead be contained within the function body. Here's the Hello World example for a reminder:

=== "Hera"

    ```py
    from hera.workflows import Steps, Workflow, WorkflowsService, script


    @script()
    def echo(message: str):
        print(message)


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

## Runner Script Templates

Hera offers a more powerful script template through the "Hera Runner", creating "runner script templates". This is where
the code is built into an OCI image, and Hera runs the module/entrypoint for you. Using the Hera Runner allows more
streamlined use of Parameters and Artifacts, which will be discussed next in the walkthrough.

We can adapt the Hello World example to use the Hera Runner: we simply add the `constructor` and `image` fields to the
script decorator.

```py
from hera.workflows import Workflow, script


@script(constructor="runner", image="my-image:v1")
def echo(message: str = "Hello world!"):
    print(message)


with Workflow(
    generate_name="hello-world-",
    entrypoint="hello",
) as w:
    echo()
```

We would then need to build `my-image:v1` using a tool like Docker, and then we will be able to run this workflow on Argo.

The YAML for the Workflow shows the changes under `script` - the `args` field in particular shows we are running the `hera.workflows.runner` module, and passing an entrypoint via `-e`. The `source` contains the input parameters, which are loaded and passed to the entrypoint:

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