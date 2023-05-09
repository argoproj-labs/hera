# Hera

```text
The Argo was constructed by the shipwright Argus,
and its crew were specially protected by the goddess Hera.
```

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/argoproj-labs/hera)

[![Build](https://github.com/argoproj-labs/hera/actions/workflows/cicd.yaml/badge.svg)](./.github/workflows/cicd.yaml)
[![Docs](https://readthedocs.org/projects/hera/badge/?version=latest)](https://hera.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/argoproj-labs/hera/branch/main/graph/badge.svg?token=x4tvsQRKXP)](https://codecov.io/gh/argoproj-labs/hera)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Pypi](https://img.shields.io/pypi/v/hera.svg)](https://pypi.python.org/pypi/hera)
[![CondaForge](https://anaconda.org/conda-forge/hera-workflows/badges/version.svg)](https://anaconda.org/conda-forge/hera-workflows)
[![Versions](https://img.shields.io/pypi/pyversions/hera.svg)](https://github.com/argoproj-labs/hera)

### Stats after the [rename to Hera](https://github.com/argoproj-labs/hera/discussions/532)

[![Downloads](https://pepy.tech/badge/hera)](https://pepy.tech/project/hera)
[![Downloads/month](https://pepy.tech/badge/hera/month)](https://pepy.tech/project/hera)
[![Downloads/week](https://pepy.tech/badge/hera/week)](https://pepy.tech/project/hera)

### Stats before the [rename to Hera](https://github.com/argoproj-labs/hera/discussions/532)

[![Downloads](https://pepy.tech/badge/hera-workflows)](https://pepy.tech/project/hera-workflows)
[![Downloads/month](https://pepy.tech/badge/hera-workflows/month)](https://pepy.tech/project/hera-workflows)
[![Downloads/week](https://pepy.tech/badge/hera-workflows/week)](https://pepy.tech/project/hera-workflows)

Hera is a Python framework for constructing and submitting Argo Workflows. The main goal of Hera is to make the Argo
ecosystem accessible by simplifying workflow construction and submission.

You can watch the introductory Hera presentation at the "Argo Workflows and Events Community Meeting 20 Oct
2021" [here](https://www.youtube.com/watch?v=QETfzfVV-GY&t=181s)!

# Table of content

- [Hera](#hera)
- [Table of content](#table-of-content)
- [Requirements](#requirements)
- [Installation](#installation)
- [Examples](#examples)
    - [Single step script](#single-step-script)
    - [DAG diamond](#dag-diamond)
- [Contributing](#contributing)
- [Comparison](#comparison)

# Requirements

Hera requires an Argo server to be deployed to a Kubernetes cluster. Currently, Hera assumes that the Argo server sits
behind an authentication layer that can authenticate workflow submission requests by using the Bearer token on the
request. To learn how to deploy Argo to your own Kubernetes cluster you can follow
the [Argo Workflows](https://argoproj.github.io/argo-workflows/quick-start/) guide!

Another option for workflow submission without the authentication layer is using port forwarding to your Argo server
deployment and submitting workflows to `localhost:2746` (2746 is the default, but you are free to use yours). Please
refer to the documentation of [Argo Workflows](https://argoproj.github.io/argo-workflows/quick-start/) to see the
command for port forward!

> **Note**
> Since the deprecation of tokens being automatically created for ServiceAccounts and Argo using Bearer tokens in place,
> it is necessary to use `--auth=server` and/or `--auth=client` when setting up Argo Workflows on Kubernetes v1.24+
> in order for hera to communicate to the Argo Server.

# Installation

## Note

Hera went through a name change - from `hera-workflows` to `hera`. This is reflected in the published
Python package. If you'd like to install versions prior to `5.0.0`, you have to use `hera-workflows`. Hera currently
publishes releases to both `hera` and `hera-workflows` for backwards compatibility purposes.

| Source                                                   | Command                                                                                              |
|----------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| [PyPi](https://pypi.org/project/hera/)                   | `pip install hera`                                                                                   |
| [PyPi](https://pypi.org/project/hera-workflows/)         | `pip install hera-workflows`                                                                         |
| [Conda](https://anaconda.org/conda-forge/hera-workflows) | `conda install -c conda-forge hera-workflows`                                                        |
| [GitHub repo](https://github.com/argoproj-labs/hera)     | `python -m pip install git+https://github.com/argoproj-labs/hera --ignore-installed`/`pip install .` |

## Optional dependencies

### yaml

- Install via `hera[yaml]`
- [PyYAML](https://pypi.org/project/PyYAML/) is required for the `yaml` output format, which is accessible via  
  `hera.workflows.Workflow.to_yaml(*args, **kwargs)`. This enables GitOps practices and easier debugging

# Examples

### Single step script

```python
from hera.workflows import Steps, Workflow, script


@script()
def echo(message: str):
    print(message)


with Workflow(
    generate_name="single-script-",
    entrypoint="steps",
) as w:
    with Steps(name="steps"):
        echo(arguments={"message": "A"})

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

See the [examples](./examples/) directory for a collection of Argo workflow construction and submission via Hera!

# Contributing

If you plan to submit contributions to Hera you can install Hera in a virtual environment managed by `poetry`:

```shell
poetry install
```

Once the dependencies are installed, you can use the various `make` targets to replicate the `CI` jobs.

```
make help
check-codegen                  Check if the code is up to date
ci                             Run all the CI checks
codegen                        Generate all the code
events-models                  Generate the Events models portion of Argo Workflows
events-service                 Generate the events service option of Hera
examples                       Generate all the examples
format                         Format and sort imports for source, tests, examples, etc.
help                           Showcase the help instructions for all the available `make` commands
lint                           Run a `lint` process on Hera and report problems
models                         Generate all the Argo Workflows models
services                       Generate the services of Hera
test                           Run tests for Hera
workflows-models               Generate the Workflows models portion of Argo Workflows
workflows-service              Generate the Workflows service option of Hera
```

Also, see the [contributing guide](./CONTRIBUTING.md)!

# Comparison

There have been other libraries available for structuring and submitting Argo Workflows:

- [Couler](https://github.com/couler-proj/couler), which aimed to provide a unified interface for constructing and
  managing workflows on different workflow engines. It has now been unmaintained since its last commit in April 2022.
- [Argo Python DSL](https://github.com/argoproj-labs/argo-python-dsl), which allows you to programmatically define Argo
  worfklows using Python. It was archived in October 2021.

While the aforementioned libraries provided amazing functionality for Argo workflow construction and submission, they
required an advanced understanding of Argo concepts. When [Dyno Therapeutics](https://dynotx.com) started using Argo
Workflows, it was challenging to construct and submit experimental machine learning workflows. Scientists and engineers
at [Dyno Therapeutics](https://dynotx.com) used a lot of time for workflow definition rather than the implementation of
the atomic unit of execution - the Python function - that performed, for instance, model training.

Hera presents an intuitive Python interface to the underlying API of Argo, with custom classes making use of context
managers and callables, empowering users to focus on their own executable payloads rather than workflow setup.

<details><summary>Here's a side by side comparison of Hera, Couler, and Argo Python DSL</summary>


You will see how Hera has focused on reducing the complexity of Argo concepts while also reducing the total lines of
code required to construct the `diamond` example, which can
be <a href="https://github.com/argoproj/argo-workflows/blob/2a9bd6c83601990259fd5162edeb425741757484/examples/dag-diamond.yaml">
found in the upstream Argo repository</a>.


<table>
<tr><th>Hera</th><th>Couler</th><th>Argo Python DSL</th></tr>
<tr>

<td valign="top"><p>

```python
from hera.workflows import DAG, Container, Parameter, Workflow

with Workflow(
    generate_name="dag-diamond-",
    entrypoint="diamond",
) as w:
    echo = Container(
        name="echo",
        image="alpine:3.7",
        command=["echo", "{{inputs.parameters.message}}"],
        inputs=[Parameter(name="message")],
    )
    with DAG(name="diamond"):
        A = echo(name="A", arguments={"message": "A"})
        B = echo(name="B", arguments={"message": "B"})
        C = echo(name="C", arguments={"message": "C"})
        D = echo(name="D", arguments={"message": "D"})
        A >> [B, C] >> D

w.create()
```

</p></td>

<td valign="top"><p>

```python
import couler.argo as couler
from couler.argo_submitter import ArgoSubmitter


def job(name):
    couler.run_container(
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=[name],
        step_name=name,
    )


def diamond():
    couler.dag(
        [
            [lambda: job(name="A")],
            [lambda: job(name="A"), lambda: job(name="B")],  # A -> B
            [lambda: job(name="A"), lambda: job(name="C")],  # A -> C
            [lambda: job(name="B"), lambda: job(name="D")],  # B -> D
            [lambda: job(name="C"), lambda: job(name="D")],  # C -> D
        ]
    )


diamond()
submitter = ArgoSubmitter()
couler.run(submitter=submitter)
```

</p></td>

<td valign="top"><p>

```python
from argo.workflows.dsl import Workflow

from argo.workflows.dsl.tasks import *
from argo.workflows.dsl.templates import *


class DagDiamond(Workflow):

    @task
    @parameter(name="message", value="A")
    def A(self, message: V1alpha1Parameter) -> V1alpha1Template:
        return self.echo(message=message)

    @task
    @parameter(name="message", value="B")
    @dependencies(["A"])
    def B(self, message: V1alpha1Parameter) -> V1alpha1Template:
        return self.echo(message=message)

    @task
    @parameter(name="message", value="C")
    @dependencies(["A"])
    def C(self, message: V1alpha1Parameter) -> V1alpha1Template:
        return self.echo(message=message)

    @task
    @parameter(name="message", value="D")
    @dependencies(["B", "C"])
    def D(self, message: V1alpha1Parameter) -> V1alpha1Template:
        return self.echo(message=message)

    @template
    @inputs.parameter(name="message")
    def echo(self, message: V1alpha1Parameter) -> V1Container:
        container = V1Container(
            image="alpine:3.7",
            name="echo",
            command=["echo", "{{inputs.parameters.message}}"],
        )

        return container
```

</p></td>
</tr>
</table>
</details>
