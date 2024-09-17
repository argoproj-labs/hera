# Quick Start

## Install in GitHub Codespaces

You can install Argo and try running Hera code in GitHub Codespaces. First, open the Hera repository in Codespaces using the link below:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/argoproj-labs/hera)

Then, you can run the `make` commands to install k3d (a lightweight Kubernetes CLI), and then install the Argo Workflows controller on the cluster:

```
make install-k3d run-argo
```

You can [take a look at `test_submission.py`](https://github.com/argoproj-labs/hera/blob/ec06876f1abc0d3309b000f3cd2e0eca64891da9/tests/test_submission.py) to see how to submit a Workflow using Hera and write your own. You can run the test Workflow using:

```
make test-on-cluster
```

See the [Viewing the Argo UI from a Codespace](../CONTRIBUTING.md#viewing-the-argo-ui-from-a-codespace) guide to see the Workflow in the UI.

Otherwise you can install the Argo CLI with

```
make install-argo
```

which will then let you do things like listing the Workflows in the `argo` namespace with

```
argo list --namespace argo
```

## Install locally

### Install Argo tools

Ensure you have a Kubernetes cluster, kubectl and Argo Workflows installed by following the
[Argo Workflows Quick Start](https://argoproj.github.io/argo-workflows/quick-start/).

Ensure you are able to submit a workflow to Argo as in the example:

```console
argo submit -n argo --watch https://raw.githubusercontent.com/argoproj/argo-workflows/master/examples/hello-world.yaml
```

### Install Hera

[![Pypi](https://img.shields.io/pypi/v/hera.svg)](https://pypi.python.org/pypi/hera)

Hera is available on PyPi as the `hera` package. Add this dependency to your project in your usual way, e.g. pip or
poetry, or install directly with `pip install hera`.

### Hello World

If you were able to run the `argo submit` command above, copy the following Workflow definition into a local file
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

w.create()
```

Run the file

```console
python -m hello_world
```

You will then see the Workflow at <https://localhost:2746/>

## Using an existing Argo installation

If you or your organization are already running on Argo and you're interested in using Hera to write your Workflow
definitions, you will need to set up some config variables in `hera.shared.global_config`. Copy the following as a basis
and fill in the blanks.

```py
from hera.workflows import Steps, Workflow, script
from hera.shared import global_config

global_config.host = "https://<your-host-name>"
global_config.token = ""  # Copy token value after "Bearer" from the `argo auth token` command
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

You will then see the Workflow at https://your-host-name
