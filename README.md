# Hera (hera-workflows)

```text
The Argo was constructed by the shipwright Argus,
and its crew were specially protected by the goddess Hera.
```
(https://en.wikipedia.org/wiki/Argo)


[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/argoproj-labs/hera-workflows)

[![Build](https://github.com/argoproj-labs/hera-workflows/actions/workflows/cicd.yaml/badge.svg)](https://github.com/argoproj-labs/hera-workflows/blob/main/.github/workflows/cicd.yaml)
[![Docs](https://readthedocs.org/projects/hera-workflows/badge/?version=latest)](https://hera-workflows.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/argoproj-labs/hera-workflows/branch/main/graph/badge.svg?token=x4tvsQRKXP)](https://codecov.io/gh/argoproj-labs/hera-workflows)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Pypi](https://img.shields.io/pypi/v/hera-workflows.svg)](https://pypi.python.org/pypi/hera-workflows)
[![CondaForge](https://anaconda.org/conda-forge/hera-workflows/badges/version.svg)](https://anaconda.org/conda-forge/hera-workflows)
[![Versions](https://img.shields.io/pypi/pyversions/hera-workflows.svg)](https://github.com/argoproj-labs/hera-workflows)

[![Downloads](https://pepy.tech/badge/hera-workflows)](https://pepy.tech/project/hera-workflows)
[![Downloads/month](https://pepy.tech/badge/hera-workflows/month)](https://pepy.tech/project/hera-workflows)
[![Downloads/week](https://pepy.tech/badge/hera-workflows/week)](https://pepy.tech/project/hera-workflows)


Hera is a Python framework for constructing and submitting Argo Workflows. The main goal of Hera is to make the Argo
ecosystem accessible by simplifying workflow construction and submission.

You can watch the introductory Hera presentation at the "Argo Workflows and Events Community Meeting 20 Oct
2021" [here](https://www.youtube.com/watch?v=QETfzfVV-GY&t=181s)!

# Table of content

- [Installation](#installation)
- [Examples](#examples)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [Comparison](#comparison)

# Requirements

Hera requires an Argo server to be deployed to a Kubernetes cluster. Currently, Hera assumes that the Argo server sits
behind an authentication layer that can authenticate workflow submission requests by using the Bearer token on the
request. To learn how to deploy Argo to your own Kubernetes cluster you can follow the
[Argo Workflows](https://argoproj.github.io/argo-workflows/quick-start/) guide!

Another option for workflow submission without the authentication layer is using port forwarding to your Argo server
deployment and submitting workflows to `localhost:2746` (2746 is the default, but you are free to use yours). Please
refer to the documentation of [Argo Workflows](https://argoproj.github.io/argo-workflows/quick-start/) to see the
command for port forward!

> **Note**
> Since the deprecation of tokens being automatically created for ServiceAccounts and Argo using Bearer tokens in place,
> it is necessary to use `--auth=server` and/or `--auth=client` when setting up Argo Workflows on Kubernetes v1.24+ 
> in order for hera-workflows to communicate to the Argo Server.

# Installation

| Source                                                         | Command                                                                                                        |
|----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|
| [PyPi](https://pypi.org/project/hera-workflows/)               | `pip install hera-workflows`                                                                                   |
| [Conda](https://anaconda.org/conda-forge/hera-workflows)       | `conda install -c conda-forge hera-workflows`                                                                  |
| [GitHub repo](https://github.com/argoproj-labs/hera-workflows) | `python -m pip install git+https://github.com/argoproj-labs/hera-workflows --ignore-installed`/`pip install .` |

# Examples

```python
from hera import Task, Workflow


def say(message: str):
    print(message)


with Workflow("diamond") as w:
    a = Task('a', say, ['This is task A!'])
    b = Task('b', say, ['This is task B!'])
    c = Task('c', say, ['This is task C!'])
    d = Task('d', say, ['This is task D!'])

    a >> [b, c] >> d

w.create()
```

See the [examples](https://github.com/argoproj-labs/hera-workflows/tree/main/examples) directory for a collection of
Argo workflow construction and submission via Hera!

# Contributing

If you plan to submit contributions to Hera you can install Hera in a virtual environment managed by `poetry`:

```shell
poetry install
```

In your activated `poetry shell`, you can utilize the tasks found in `tox.ini`, e.g.:

To run tests on all supported python versions with coverage run [tox](https://tox.wiki/en/latest/):

```shell
tox
```

To list all available `tox` envs run:

```shell
tox -a
```

To run selected tox envs, e.g. for a specific python version with coverage run:

```shell
tox -e py37,coverage
```

As `coverage` *depends* on `py37`, it will run *after* `py37`

See project `tox.ini` for more details

Also, see the [contributing guide](https://github.com/argoproj-labs/hera-workflows/blob/main/CONTRIBUTING.md)!

# Comparison

There are other libraries currently available for structuring and submitting Argo Workflows:

- [Couler](https://github.com/couler-proj/couler), which aims to provide a unified interface for constructing and
  managing workflows on different workflow engines;
- [Argo Python DSL](https://github.com/argoproj-labs/argo-python-dsl), which allows you to programmaticaly define Argo
  worfklows using Python.

While the aforementioned libraries provide amazing functionality for Argo workflow construction and submission, they
require an advanced understanding of Argo concepts. When [Dyno Therapeutics](https://dynotx.com) started using Argo
Workflows, it was challenging to construct and submit experimental machine learning workflows. Scientists and engineers
at [Dyno Therapeutics](https://dynotx.com) used a lot of time for workflow definition rather than the implementation of
the atomic unit of execution - the Python function - that performed, for instance, model training.

Hera presents a much simpler interface for task and workflow construction, empowering users to focus on their own
executable payloads rather than workflow setup. Here's a side by side comparison of Hera, Argo Python DSL, and Couler:

<table>
<tr><th>Hera</th><th>Couler</th><th>Argo Python DSL</th></tr>
<tr>

<td valign="top"><p>

```python
from hera import Task, Workflow


def say(message: str):
    print(message)


with Workflow("diamond") as w:
    a = Task('a', say, ['This is task A!'])
    b = Task('b', say, ['This is task B!'])
    c = Task('c', say, ['This is task C!'])
    d = Task('d', say, ['This is task D!'])

    a >> [b, c] >> d

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
