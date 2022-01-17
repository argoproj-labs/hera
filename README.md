# Hera (hera-workflows)

```text
The Argo was constructed by the shipwright Argus, and its crew were specially protected by the goddess Hera.
```

(https://en.wikipedia.org/wiki/Argo)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Hera is a Python framework for constructing and submitting Argo Workflows. The main goal of Hera is to make Argo
Workflows more accessible by abstracting away some setup that is typically necessary for constructing workflows.

Python functions are first class citizens in Hera - they are the atomic units (execution payload) that are submitted for
remote execution. The framework makes it easy to wrap execution payloads into Argo Workflow tasks, set dependencies,
resources, etc.

You can watch the introductory Hera presentation at the "Argo Workflows and Events Community Meeting 20 Oct
2021" [here](https://www.youtube.com/watch?v=QETfzfVV-GY&t=181s)!

# Table of content

- [Assumptions](#assumptions)
- [Installation](#installation)
- [Contributing](#contributing)
- [Concepts](#concepts)
- [Examples](#examples)
- [Comparison](#comparison)

# Assumptions

Hera is exclusively dedicated to remote workflow submission and execution. Therefore, it requires an Argo server to be
deployed to a Kubernetes cluster. Currently, Hera assumes that the Argo server sits behind an authentication layer that
can authenticate workflow submission requests by using the Bearer token on the request. To learn how to deploy Argo to
your own Kubernetes cluster you can follow the
[Argo Workflows](https://argoproj.github.io/argo-workflows/quick-start/) guide!

Another option for workflow submission without the authentication layer is using port forwarding to your Argo server
deployment and submitting workflows to `localhost:2746` (2746 is the default, but you are free to use yours). Please
refer to the documentation of [Argo Workflows](https://argoproj.github.io/argo-workflows/quick-start/) to see the
command for port forward!

In the future some of these assumptions may either increase or decrease depending on the direction of the project. Hera
is mostly designed for practical data science purposes, which assumes the presence of a DevOps team to set up an Argo
server for workflow submission.

# Installation

There are multiple ways to install Hera:

1. You can install from [PyPi](https://pypi.org/project/hera-workflows/):

  ```shell
  pip install hera-workflows
  ```

2. Install it directly from this repository using:

  ```shell
  python -m pip install git+https://github.com/argoproj-labs/hera-workflows --ignore-installed
  ```

3. Alternatively, you can clone this repository and then run the following to install:

  ```shell
  python setup.py install
  ```

# Contributing

If you plan to submit contributions to Hera you can install Hera in a virtual environment managed by `pipenv`:

```shell
pipenv shell
pipenv sync --dev --pre
```

Also, see the [contributing guide](https://github.com/argoproj-labs/hera-workflows/blob/main/CONTRIBUTING.md)!

# Concepts

Currently, Hera is centered around two core concepts. These concepts are also used by Argo, which Hera aims to stay
consistent with:

- `Task` - the object that holds the Python function for remote execution/the atomic unit of execution;
- `Workflow` - the higher level representation of a collection of tasks.

# Examples

A very primitive example of submitting a task within a workflow through Hera is:

```python
from hera.task import Task
from hera.workflow import Workflow
from hera.workflow_service import WorkflowService


def say(message: str):
    """
    This can be anything as long as the Docker image satisfies the dependencies. You can import anything Python 
    that is in your container e.g torch, tensorflow, scipy, biopython, etc - just provide an image to the task!
    """
    print(message)


ws = WorkflowService('my-argo-domain.com', 'my-argo-server-token')
w = Workflow('my-workflow', ws)
t = Task('say', say, [{'message': 'Hello, world!'}])
w.add_task(t)
w.submit()
```

See the [examples](https://github.com/argoproj-labs/hera-workflows/tree/main/examples) directory for a collection of
Argo workflow construction and submission via Hera!

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
from hera.task import Task
from hera.workflow import Workflow
from hera.workflow_service import WorkflowService


def say(message: str):
    print(message)


ws = WorkflowService('my-argo-server.com', 'my-auth-token')
w = Workflow('diamond', ws)
a = Task('A', say, [{'message': 'This is task A!'}])
b = Task('B', say, [{'message': 'This is task B!'}])
c = Task('C', say, [{'message': 'This is task C!'}])
d = Task('D', say, [{'message': 'This is task D!'}])

a.next(b).next(d)  # a >> b >> d
a.next(c).next(d)  # a >> c >> d

w.add_tasks(a, b, c, d)
w.submit()
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
