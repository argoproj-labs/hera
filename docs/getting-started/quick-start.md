# Quick Start

# Install Argo tools

Ensure you have a Kubernetes cluster, kubectl and Argo Workflows installed by following the
[Argo Workflows Quick Start](https://argoproj.github.io/argo-workflows/quick-start/).

Ensure you are able to submit a workflow to Argo as in the example:

```
argo submit -n argo --watch https://raw.githubusercontent.com/argoproj/argo-workflows/master/examples/hello-world.yaml
```

# Install Hera
[![Pypi](https://img.shields.io/pypi/v/hera.svg)](https://pypi.python.org/pypi/hera)

Hera is available on PyPi as the `hera` package. Add this dependency to your project in your usual way, e.g. pip or
poetry, or install directly with `pip install hera`.

# Hello World
Copy the following Workflow definition into a local file `hello_world.py`.

```py
from hera.workflows import Steps, Workflow, script


@script()
def echo(message: str):
    print(message)


with Workflow(
    generate_name="hello-world-",
    entrypoint="steps",
    namespace="argo",
) as w:
    with Steps(name="steps"):
        echo(arguments={"message": "Hello world!"})

w.create()
```

Run the file
```
python -m hello_world.py
```
