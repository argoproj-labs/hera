# Artifacts

In Argo Workflows, Artifacts are mainly used for inputs and outputs that are very large, or are binary files. For
outputs, Argo exports a file from the container as an Artifact. Inputs are loaded into the container.

In most cases, you should prefer to use [Parameters](./parameters.md). In Hera, by using the Hera Runner, Artifacts are
as easy to use as Parameters!

> **Note:** you should refer to the Argo's
> [Configuring Your Artifact Repository](https://argoproj.github.io/argo-workflows/configure-artifact-repository/) page
> to be able to run Artifact examples

## Artifacts for Runner Scripts

Using the Hera Runner is highly recommended for Artifacts, as the Runner handles the loading and saving of Artifacts for
you, letting you concentrate on the business logic instead of writing files to the correct locations! For Runner
scripts, the only difference between Parameters and Artifacts is the annotation.

### Runner Artifact Outputs

For Output Artifacts, you simply need to annotate the return type using `Annotated` (and remember to give your
`Artifact` a name):

```py
@script(constructor="runner", image="my-image:v1")
def whalesay() -> Annotated[str, Artifact(name="hello-art")]:
    return "Hello world!"
```

Multiple Artifacts can be exported as a tuple:

```py
@script(constructor="runner", image="my-image:v1")
def whalesay() -> Tuple[
    Annotated[str, Artifact(name="hello-art")],
    Annotated[str, Artifact(name="goodbye-art")],
]:
    return "Hello world!", "Goodbye world!"
```

If you have many outputs, consider using the [Runner IO feature](../user-guides/script-runner-io.md) to avoid a long
tuple return, instead using named arguments in the return.

### Runner Artifact Inputs

Input Artifacts require a similar annotation (name is optional):

```py
@script(constructor="runner", image="my-image:v1")
def whalesay(message: Annotated[str, Artifact(name="hello-art")]):
    print(message)
```

Using multiple input Artifacts is as easy as adding multiple function arguments:

```py
@script(constructor="runner", image="my-image:v1")
def whalesay(
    message_1: Annotated[str, Artifact(name="hello-art")],
    message_2: Annotated[str, Artifact(name="hello-art-2")],
):
    ...
```

## Artifacts for Inline Scripts

Here, we are looking at the [Script Artifact Passing](../examples/workflows/scripts/script_artifact_passing.md) example.

> **Note:** Artifacts are more verbose and harder to use in Inline scripts, we highly recommend using
> [Runner Scripts](#artifacts-for-runner-scripts) if possible!

<details><summary>Click here to see the full example
</summary>

```py
from hera.workflows import Artifact, Steps, Workflow, script


@script(outputs=Artifact(name="hello-art", path="/tmp/hello_world.txt"))
def whalesay():
    with open("/tmp/hello_world.txt", "w") as f:
        f.write("hello world")


@script(inputs=Artifact(name="message", path="/tmp/message"))
def print_message():
    with open("/tmp/message", "r") as f:
        message = f.readline()
    print(message)


with Workflow(generate_name="artifact-passing-", entrypoint="artifact-example") as w:
    with Steps(name="artifact-example") as s:
        ga = whalesay(name="generate-artifact")
        print_message(name="consume-artifact", arguments=ga.get_artifact("hello-art").as_name("message"))
```

</details>


### Inline Artifact Outputs

Artifact outputs work by exporting a file from the container. In this case, we will output the file
`/tmp/hello_world.txt`. First we need to specify this path in the script decorator:

```py
@script(outputs=Artifact(name="hello-art", path="/tmp/hello_world.txt"))
def whalesay():
    ...
```

We then write to the specified path within the function:

```py
@script(outputs=Artifact(name="hello-art", path="/tmp/hello_world.txt"))
def whalesay():
    with open("/tmp/hello_world.txt", "w") as f:
        f.write("hello world")
```

We can then call the function in a Steps context. Compare to the YAML workflow and see the logs below:

=== "Hera"

    ```py
    with Workflow(generate_name="artifact-passing-", entrypoint="artifact-example") as w:
        with Steps(name="artifact-example") as s:
            ga = whalesay(name="generate-artifact")
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: artifact-passing-
    spec:
      entrypoint: artifact-example
      templates:
      - name: artifact-example
        steps:
        - - name: generate-artifact
            template: whalesay
      - name: whalesay
        outputs:
          artifacts:
          - name: hello-art
            path: /tmp/hello_world.txt
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            with open('/tmp/hello_world.txt', 'w') as f:
                f.write('hello world')
          command:
          - python
    ```

=== "Logs"

    ```console
    artifact-passing-jkrwh-whalesay-8621968: time="2023-05-31T09:11:30.307Z" level=info msg="sub-process exited" argo=true error="<nil>"
    artifact-passing-jkrwh-whalesay-8621968: time="2023-05-31T09:11:30.307Z" level=info msg="/tmp/hello_world.txt -> /var/run/argo/outputs/artifacts/tmp/hello_world.txt.tgz" ar
    go=true
    artifact-passing-jkrwh-whalesay-8621968: time="2023-05-31T09:11:30.307Z" level=info msg="Taring /tmp/hello_world.txt"
    ```

### Inline Artifact Inputs

When we have one step generating an Artifact, we'd usually like to consume it in a downstream task. We do this with the
`get_artifact` function that exists for `Steps` and `Tasks`.

First, let's create a function that takes in an Artifact:

```py
@script(inputs=Artifact(name="message", path="/tmp/message"))
def print_message():
    ...
```

Argo Workflows will mount any input artifact to the specified path. In this case, whatever artifact is passed in through
the `message` argument is mounted to the path `/tmp/message`. Here, we just want to echo what was in the artifact:

```py
@script(inputs=Artifact(name="message", path="/tmp/message"))
def print_message():
    with open("/tmp/message", "r") as f:
        message = f.readline()
    print(message)
```

Now, we can call this function as a `Step` or `Task`, expanding on our Workflow started earlier. We pass the `hello-art`
output artifact as the `message` input artifact:

=== "Hera"

    ```py
    with Workflow(generate_name="artifact-passing-", entrypoint="artifact-example") as w:
        with Steps(name="artifact-example") as s:
            ga = whalesay(name="generate-artifact")
            print_message(
                name="consume-artifact",
                arguments={"message": ga.get_artifact("hello-art")},
            )
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: artifact-passing-
    spec:
      entrypoint: artifact-example
      templates:
      - name: artifact-example
        steps:
        - - name: generate-artifact
            template: whalesay
        - - name: consume-artifact
            template: print-message
            arguments:
              artifacts:
              - name: message
                from: '{{steps.generate-artifact.outputs.artifacts.hello-art}}'
      - name: whalesay
        outputs:
          artifacts:
          - name: hello-art
            path: /tmp/hello_world.txt
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            with open('/tmp/hello_world.txt', 'w') as f:
                f.write('hello world')
          command:
          - python
      - name: print-message
        inputs:
          artifacts:
          - name: message
            path: /tmp/message
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            with open('/tmp/message', 'r') as f:
                message = f.readline()
            print(message)
          command:
          - python
    ```

=== "Logs"

    ```console
    artifact-passing-s7xrb-whalesay-751687878: time="2023-05-31T09:22:50.999Z" level=info msg="sub-process exited" argo=true error="<nil>"
    artifact-passing-s7xrb-whalesay-751687878: time="2023-05-31T09:22:50.999Z" level=info msg="/tmp/hello_world.txt -> /var/run/argo/outputs/artifacts/tmp/hello_world.txt.tgz"
    argo=true
    artifact-passing-s7xrb-whalesay-751687878: time="2023-05-31T09:22:50.999Z" level=info msg="Taring /tmp/hello_world.txt"
    artifact-passing-s7xrb-print-message-154872134: hello world
    artifact-passing-s7xrb-print-message-154872134: time="2023-05-31T09:23:01.204Z" level=info msg="sub-process exited" argo=true error="<nil>"
    ```
