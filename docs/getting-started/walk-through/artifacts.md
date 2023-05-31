# Artifacts

**Note:** you should refer to the Argo's
[Configuring Your Artifact Repository](https://argoproj.github.io/argo-workflows/configure-artifact-repository/) page to
be able to run Artifact examples

Artifacts are mainly used for outputs that are very large or are of non-text file types.

## Artifacts in Hera

Here, we are looking at the [Script Artifact Passing](../../examples/workflows/script_artifact_passing.md) example.

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


### Artifacts as Output

We want to output a file `/tmp/hello_world.txt` from a function. To do this, we need to tell the `script` decorator
through its `outputs` member that we will output an `Artifact`. This tells Argo to expect a file at the given `path`, so
that when the Workflow is submitted, it can export the file from the container running our script. We also give the
`Artifact` a name that other `Steps` or `Tasks` can refer to, but is not relevant to the function itself.

```py
@script(outputs=Artifact(name="hello-art", path="/tmp/hello_world.txt"))
def whalesay():
    ...
```

Once we have specified the `Artifact` that Argo will export from this script, we can fill out the function, writing a
file to the specified path.

```py
@script(outputs=Artifact(name="hello-art", path="/tmp/hello_world.txt"))
def whalesay():
    with open("/tmp/hello_world.txt", "w") as f:
        f.write("hello world")
```

In the Steps, we can then call the function, and if you run this Workflow, you'll see the artifact is generated.

```py
with Workflow(generate_name="artifact-passing-", entrypoint="artifact-example") as w:
    with Steps(name="artifact-example") as s:
        ga = whalesay(name="generate-artifact")
```

The log for the Workflow so far will show

```console
artifact-passing-jkrwh-whalesay-8621968: time="2023-05-31T09:11:30.307Z" level=info msg="sub-process exited" argo=true error="<nil>"
artifact-passing-jkrwh-whalesay-8621968: time="2023-05-31T09:11:30.307Z" level=info msg="/tmp/hello_world.txt -> /var/run/argo/outputs/artifacts/tmp/hello_world.txt.tgz" ar
go=true
artifact-passing-jkrwh-whalesay-8621968: time="2023-05-31T09:11:30.307Z" level=info msg="Taring /tmp/hello_world.txt"
```


### Artifacts as Input - Passing Artifacts

When we have one step generating an Artifact, we'd usually like to consume it in a downstream task, unless it's part of
the final outputs of a Workflow. We do this with the `get_artifact` function that exists for `Steps` and `Tasks`.

First, let's create a function that takes in an Artifact.


```py
@script(inputs=Artifact(name="message", path="/tmp/message"))
def print_message():
    ...
```

Specifying an Artifact in the inputs means the Kubernetes container running this script will mount Artifacts that are
passed as arguments to `Steps` or `Tasks`. In this case, whatever artifact is passed in through the `message` argument
is mounted to the path `/tmp/message`. Here, we just want to echo what was in the artifact.

```py
@script(inputs=Artifact(name="message", path="/tmp/message"))
def print_message():
    with open("/tmp/message", "r") as f:
        message = f.readline()
    print(message)
```

Now, we can call this function as a `Step` or `Task`, expanding on our Workflow started earlier. We pass the `hello-art`
output artifact as the `message` input artifact.

```py
with Workflow(generate_name="artifact-passing-", entrypoint="artifact-example") as w:
    with Steps(name="artifact-example") as s:
        ga = whalesay(name="generate-artifact")
        print_message(
            name="consume-artifact",
            arguments=ga.get_artifact("hello-art").as_name("message"),
        )
```

The logs when running the full Workflow will look like

```console
artifact-passing-s7xrb-whalesay-751687878: time="2023-05-31T09:22:50.999Z" level=info msg="sub-process exited" argo=true error="<nil>"
artifact-passing-s7xrb-whalesay-751687878: time="2023-05-31T09:22:50.999Z" level=info msg="/tmp/hello_world.txt -> /var/run/argo/outputs/artifacts/tmp/hello_world.txt.tgz"
argo=true
artifact-passing-s7xrb-whalesay-751687878: time="2023-05-31T09:22:50.999Z" level=info msg="Taring /tmp/hello_world.txt"
artifact-passing-s7xrb-print-message-154872134: hello world
artifact-passing-s7xrb-print-message-154872134: time="2023-05-31T09:23:01.204Z" level=info msg="sub-process exited" argo=true error="<nil>"
```
