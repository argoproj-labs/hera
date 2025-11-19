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

Here, we are looking at the [Basic Artifacts](../examples/workflows/artifacts/basic_artifacts.md) example.

> **Note:** Artifacts are more verbose and harder to use in Inline scripts, we highly recommend using
> [Runner Scripts](#artifacts-for-runner-scripts) if possible!

<details><summary>Click here to see the full example
</summary>

```py
from hera.workflows import Artifact, NoneArchiveStrategy, Steps, Workflow, script


@script(outputs=Artifact(name="out-art", path="/tmp/file", archive=NoneArchiveStrategy()))
def writer():
    with open("/tmp/file", "w") as f:
        f.write("Hello, world!")


@script(inputs=Artifact(name="in-art", path="/tmp/file"))
def consumer():
    with open("/tmp/file", "r") as f:
        print(f.readlines())  # prints `Hello, world!` to `stdout`


with Workflow(generate_name="artifact-", entrypoint="steps") as w:
    with Steps(name="steps"):
        w_ = writer()
        c = consumer(arguments={"in-art": w_.get_artifact("out-art")})
```
</details>


### Inline Artifact Outputs

Artifact outputs work by exporting a file from the container. In this case, we will output the file
`/tmp/file`. First we need to specify this path in the script decorator:

```py
@script(outputs=Artifact(name="out-art", path="/tmp/file", archive=NoneArchiveStrategy()))
def writer():
    ...
```

We then write to the specified path within the function:

```py
@script(outputs=Artifact(name="out-art", path="/tmp/file", archive=NoneArchiveStrategy()))
def writer():
    with open("/tmp/file", "w") as f:
        f.write("Hello, world!")
```

We can then call the function in a Steps context. Compare to the YAML workflow and see the logs below:

=== "Hera"

    ```py
    with Workflow(generate_name="artifact-", entrypoint="steps") as w:
        with Steps(name="steps"):
            w_ = writer()
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: artifact-
    spec:
      entrypoint: steps
      templates:
      - name: steps
        steps:
        - - name: writer
            template: writer
        - - name: consumer
            template: consumer
            arguments:
              artifacts:
              - name: in-art
                from: '{{steps.writer.outputs.artifacts.out-art}}'
      - name: writer
        outputs:
          artifacts:
          - name: out-art
            path: /tmp/file
            archive:
              none: {}
        script:
          image: python:3.10
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            with open('/tmp/file', 'w') as f:
                f.write('Hello, world!')
          command:
          - python
    ```

=== "Logs"

    ```console
    artifact-bj4zh-writer-3078707681: time="2025-06-10T14:58:08 UTC" level=info msg="capturing logs" argo=true
    artifact-bj4zh-writer-3078707681: time="2025-06-10T14:58:09 UTC" level=info msg="sub-process exited" argo=true error="<nil>"
    artifact-bj4zh-writer-3078707681: time="2025-06-10T14:58:09 UTC" level=info msg="/tmp/file -> /var/run/argo/outputs/artifacts/tmp/file.tgz" argo=true
    artifact-bj4zh-writer-3078707681: time="2025-06-10T14:58:09 UTC" level=info msg="Taring /tmp/file"
    ```

### Inline Artifact Inputs

When we have one step generating an Artifact, we'd usually like to consume it in a downstream task. We do this with the
`get_artifact` function that exists for `Steps` and `Tasks`.

First, let's create a function that takes in an Artifact:

```py
@script(inputs=Artifact(name="in-art", path="/tmp/file"))
def consumer():
```

Argo Workflows will mount any input artifact to the specified path. In this case, whatever artifact is passed in through
the `in-art` Artifact is mounted to the path `/tmp/file`. Here, we just want to echo what was in the artifact:

```py
@script(inputs=Artifact(name="in-art", path="/tmp/file"))
def consumer():
    with open("/tmp/file", "r") as f:
        print(f.readlines())  # prints `Hello, world!` to `stdout`

```

Now, we can call this function as a `Step` or `Task`, expanding on our Workflow started earlier. We pass the `out-art`
output artifact to the `in-art` input artifact:

=== "Hera"

    ```py
    with Workflow(generate_name="artifact-", entrypoint="steps") as w:
        with Steps(name="d"):
            w_ = writer()
            c = consumer(arguments={"in-art": w_.get_artifact("out-art")})
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: artifact-
    spec:
      entrypoint: steps
      templates:
      - name: steps
        steps:
        - - name: writer
            template: writer
        - - name: consumer
            template: consumer
            arguments:
              artifacts:
              - name: in-art
                from: '{{steps.writer.outputs.artifacts.out-art}}'
      - name: writer
        outputs:
          artifacts:
          - name: out-art
            path: /tmp/file
            archive:
              none: {}
        script:
          image: python:3.10
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            with open('/tmp/file', 'w') as f:
                f.write('Hello, world!')
          command:
          - python
      - name: consumer
        inputs:
          artifacts:
          - name: in-art
            path: /tmp/file
        script:
          image: python:3.10
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            with open('/tmp/file', 'r') as f:
                print(f.readlines())
          command:
          - python
    ```

=== "Logs"

    ```console
    artifact-bghf5-writer-3091035417: time="2025-06-10T15:14:24 UTC" level=info msg="capturing logs" argo=true
    artifact-bghf5-writer-3091035417: time="2025-06-10T15:14:25 UTC" level=info msg="sub-process exited" argo=true error="<nil>"
    artifact-bghf5-writer-3091035417: time="2025-06-10T15:14:25 UTC" level=info msg="/tmp/file -> /var/run/argo/outputs/artifacts/tmp/file.tgz" argo=true
    artifact-bghf5-writer-3091035417: time="2025-06-10T15:14:25 UTC" level=info msg="Taring /tmp/file"
    artifact-bghf5-consumer-1167317153: time="2025-06-10T15:14:34 UTC" level=info msg="capturing logs" argo=true
    artifact-bghf5-consumer-1167317153: ['Hello, world!']
    artifact-bghf5-consumer-1167317153: time="2025-06-10T15:14:35 UTC" level=info msg="sub-process exited" argo=true error="<nil>"
    ```
