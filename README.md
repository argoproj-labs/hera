# Hera

Hera is a Python framework for constructing and submitting Argo Workflows. The main goal of Hera is to make the Argo
ecosystem accessible by simplifying workflow construction and submission.

[See the Quick Start guide](https://hera.readthedocs.io/en/stable/walk-through/quick-start/) to start using Hera to
orchestrate your Argo Workflows!

```text
The Argo was constructed by the shipwright Argus,
and its crew were specially protected by the goddess Hera.
```

## Links

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/argoproj-labs/hera)

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/argoproj-labs/hera)

[![CICD](https://github.com/argoproj-labs/hera/actions/workflows/cicd.yaml/badge.svg)](https://github.com/argoproj-labs/hera/actions/workflows/cicd.yaml)
[![Docs](https://readthedocs.org/projects/hera/badge/?version=latest)](https://hera.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/argoproj-labs/hera/branch/main/graph/badge.svg?token=x4tvsQRKXP)](https://codecov.io/gh/argoproj-labs/hera)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Pypi](https://img.shields.io/pypi/v/hera.svg)](https://pypi.python.org/pypi/hera)
[![Versions](https://img.shields.io/pypi/pyversions/hera.svg)](https://github.com/argoproj-labs/hera)

[![CondaForge](https://anaconda.org/conda-forge/hera-workflows/badges/version.svg)](https://anaconda.org/conda-forge/hera-workflows)

### PyPi stats for `hera`

[![Downloads](https://static.pepy.tech/badge/hera)](https://pepy.tech/project/hera)
[![Downloads/month](https://static.pepy.tech/badge/hera/month)](https://pepy.tech/project/hera)
[![Downloads/week](https://static.pepy.tech/badge/hera/week)](https://pepy.tech/project/hera)

### PyPi stats for `hera-workflows`

> **⚠ Note ⚠** The `hera-workflows` package is **deprecated** since the project
> [renamed to Hera](https://github.com/argoproj-labs/hera/discussions/532) for V5. Please install from the `hera` PyPi
> package.

[![Downloads](https://static.pepy.tech/badge/hera-workflows)](https://pepy.tech/project/hera-workflows)
[![Downloads/month](https://static.pepy.tech/badge/hera-workflows/month)](https://pepy.tech/project/hera-workflows)
[![Downloads/week](https://static.pepy.tech/badge/hera-workflows/week)](https://pepy.tech/project/hera-workflows)

## Hera at a glance

### Steps diamond

```python
from hera.workflows import Steps, Workflow, script

@script()
def echo(message: str):
    print(message)

with Workflow(
    generate_name="single-script-",
    entrypoint="steps",
) as w:
    with Steps(name="steps") as s:
        echo(name="A", arguments={"message": "I'm a step"})
        with s.parallel():
            echo(name="B", arguments={"message": "We're steps"})
            echo(name="C", arguments={"message": "in parallel!"})
        echo(name="D", arguments={"message": "I'm another step!"})

w.create()
```

### DAG diamond

```python
from hera.workflows import DAG, Workflow, script

@script()
def echo(message: str):
    print(message)

with Workflow(
    generate_name="dag-diamond-",
    entrypoint="diamond",
) as w:
    with DAG(name="diamond"):
        A = echo(name="A", arguments={"message": "A"})
        B = echo(name="B", arguments={"message": "B"})
        C = echo(name="C", arguments={"message": "C"})
        D = echo(name="D", arguments={"message": "D"})
        A >> [B, C] >> D

w.create()
```

See the [examples](./examples/workflows-examples.md) for a collection of Argo workflow construction and submission via Hera!

## Requirements

Hera requires an Argo server to be deployed to a Kubernetes cluster. Currently, Hera assumes that the Argo server sits
behind an authentication layer that can authenticate workflow submission requests by using the Bearer token on the
request. To learn how to deploy Argo to your own Kubernetes cluster you can follow
the [Argo Workflows](https://argoproj.github.io/argo-workflows/quick-start/) guide!

Another option for workflow submission without the authentication layer is using port forwarding to your Argo server
deployment and submitting workflows to `localhost:2746` (2746 is the default, but you are free to change it). Please
refer to the documentation of [Argo Workflows](https://argoproj.github.io/argo-workflows/quick-start/) to see the
command for port forward!

> **Note** Since the deprecation of tokens being automatically created for ServiceAccounts and Argo using Bearer tokens
> in place, it is necessary to use `--auth=server` and/or `--auth=client` when setting up Argo Workflows on Kubernetes
> v1.24+ in order for hera to communicate to the Argo Server.

### Authenticating in Hera

There are a few ways to authenticate in Hera - read more in the
[authentication walk through](https://hera.readthedocs.io/en/stable/walk-through/authentication/) - for now, with the
`argo` cli tool installed, this example will get you up and running:

```py
from hera.workflows import Workflow, Container
from hera.shared import global_config
from hera.auth import ArgoCLITokenGenerator

global_config.host = "http://localhost:2746"
global_config.token = ArgoCLITokenGenerator

with Workflow(generate_name="local-test-", entrypoint="c") as w:
    Container( name="c", image="docker/whalesay", command=["cowsay", "hello"])

w.create()
```

## Installation

> **Note** Hera went through a name change - from `hera-workflows` to `hera`. This is reflected in the published Python
> package. If you'd like to install versions prior to `5.0.0`, you have to use `hera-workflows`. Hera currently
> publishes releases to both `hera` and `hera-workflows` for backwards compatibility purposes.

| Source                                                   | Command                                                                                              |
|----------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| [PyPi](https://pypi.org/project/hera/)                   | `pip install hera`                                                                                   |
| [PyPi](https://pypi.org/project/hera-workflows/)         | `pip install hera-workflows`                                                                         |
| [Conda](https://anaconda.org/conda-forge/hera-workflows) | `conda install -c conda-forge hera-workflows`                                                        |
| [GitHub repo](https://github.com/argoproj-labs/hera)     | `python -m pip install git+https://github.com/argoproj-labs/hera --ignore-installed`/`pip install .` |

### Optional dependencies

#### yaml

- Install via `hera[yaml]`
- [PyYAML](https://pypi.org/project/PyYAML/) is required for the `yaml` output format, which is accessible via
  `hera.workflows.Workflow.to_yaml(*args, **kwargs)`. This enables GitOps practices and easier debugging.

## Presentations

- [Argo Workflows and Events Community Meeting 20 Oct 2021 - Hera introductory presentation](https://youtu.be/QETfzfVV-GY?t=181)
- [Argo Workflows and Events Community Meeting 15 June 2022 - Hera project update](https://youtu.be/sdkBDPOdQ-g?t=231)
- [KubeCon/ArgoCon EU 2023 - Scaling gene therapy with Argo Workflows and Hera](https://www.youtube.com/watch?v=h2TEw8kd1Ds)
- [DoKC Town Hall #2 - Unsticking ourselves from Glue - Migrating PayIt's Data Pipelines to Argo Workflows and Hera](https://youtu.be/sSLFVIIEKcE?t=2088)
- [KubeCon / ArgoCon NA 2023 - How to Train an LLM with Argo Workflows and Hera](https://www.youtube.com/watch?v=nRYf3GkKpss&ab_channel=CNCF%5BCloudNativeComputingFoundation%5D)
    - [Featured code](https://github.com/flaviuvadan/kubecon_na_23_llama2_finetune)
- [CNCF TAG App-Delivery @ KubeCon NA 2023 - Automating the Deployment of Data Workloads to Kubernetes with ArgoCD, Argo Workflows, and Hera](https://www.youtube.com/watch?v=NZCmYRVziGY&t=12481s&ab_channel=CNCFTAGAppDelivery)

## Blogs

- [Hera introduction and motivation](https://www.dynotx.com/hera-the-missing-argo-workflows-python-sdk/)
- [Dyno is scaling gene therapy research with cloud-native tools like Argo Workflows and Hera](https://www.dynotx.com/argo-workflows-hera/)

## Contributing

See the [contributing guide](./CONTRIBUTING.md)!
