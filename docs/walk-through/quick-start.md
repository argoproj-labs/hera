# Quick Start

## Install Hera

[![Pypi](https://img.shields.io/pypi/v/hera.svg)](https://pypi.python.org/pypi/hera)

Hera is available on PyPi as the `hera` package. Add this dependency to your project with your favourite package
manager, e.g. [poetry](https://python-poetry.org/), or install directly with
[pip](https://packaging.python.org/en/latest/guides/tool-recommendations/#installing-packages):

```
pip install hera
```

## Install Argo Workflows

Hera is a Python SDK built for Argo Workflows, which runs on Kubernetes, therefore you will need a Kubernetes
environment to run Argo Workflows and test out Hera. If you already have an existing Argo Workflows installation, you
can go straight to [Running Workflows from Hera](#running-workflows-from-hera) below.

### Install Locally

If you want to run on a local Kubernetes cluster (e.g. Docker Desktop), follow the
[Argo Workflows Quick Start guide](https://argoproj.github.io/argo-workflows/quick-start/).

Ensure you are able to submit a workflow to Argo as in the example:

```console
argo submit -n argo --watch https://raw.githubusercontent.com/argoproj/argo-workflows/master/examples/hello-world.yaml
```

Use the following command to port-forward the Argo Server; this allows you to access the UI and submit Workflows from
Hera:

```console
kubectl -n argo port-forward service/argo-server 2746:2746
```

Check that you can see the UI at <https://localhost:2746>.

Then go to [Running Workflows from Hera](#running-workflows-from-hera) below.

## Running Workflows from Hera

### Local Argo Workflows Installation

Copy the following Workflow definition into a local file
`hello_world.py`.

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

submitted_workflow = w.create()
print(f"Workflow at https://localhost:2746/workflows/argo/{submitted_workflow.metadata.name}")
```

Run the file

```console
python -m hello_world
```

You will then see the Workflow at the specified link.

### Existing Cloud Installation of Argo Workflows

If you or your organization are already running on Argo and you're interested in using Hera to write your Workflow
definitions, you will need to set up some config variables in `hera.shared.global_config`. Copy the following into a
local file as a basis and fill in the blanks.

```py
from hera.workflows import Steps, Workflow, script
from hera.shared import global_config

global_config.host = "https://<your-host-name>"
global_config.token = ""  # Copy token value after "Bearer" from the CLI command `argo auth token`
global_config.image = "<your-image-repository>/python:3.9"  # Set the image if you cannot access "python:3.9" via Docker Hub


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

```console
python -m hello_world
```

You will then see the Workflow at `https://<your-host-name>`
