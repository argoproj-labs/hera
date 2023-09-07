# History of Hera

## Comparison

There have been other libraries available for structuring and submitting Argo Workflows:

- [Couler](https://github.com/couler-proj/couler), which aimed to provide a unified interface for constructing and
  managing workflows on different workflow engines. It is now officially unmaintained.
- [Argo Python DSL](https://github.com/argoproj-labs/argo-python-dsl), which allows you to programmatically define Argo
  worfklows using Python. The GitHub repository was archived in October 2021.

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

## Hera V5 vs V4

_Reserving here for Bloomberg history with Argo/Hera._

Hera v5 is a major release that introduces breaking changes from v4. The main reason for this is that v5 is a complete
rewrite of the library, and is now based on the OpenAPI specification of Argo Workflows. This allows us to provide a
more intuitive interface to the Argo API, while also providing full feature parity with Argo Workflows. This means that
you can now use all the features of Argo Workflows in your workflows. Additionally, it has been re-structured to
accommodate other Argo projects, such as Argo Events and Argo CD. Currently only Argo Workflows is supported, and there
is some work in progress to add support for Argo Events.

The codebase is now much more readable, and the focus can be fully dedicated to improving the Python interface to
various Argo projects rather than maintaining feature parity with the Argo codebase. The library is divided into the
following components:

- `hera.shared` - This package contains the shared code that will be used by all Argo projects. This includes common
  global configuration to interact with the Argo API, and common Pydantic base models that are used by all Argo
  projects.

- `hera.events.models` - This package contains the auto-generated code that allows you to construct Argo Events. It
  provides Pydantic models for all the Argo Events OpenAPI objects, and allows you to construct events using these
  models. These models are based on the OpenAPI specification, and are therefore exactly the same as the models used by
  Argo Events.

- `hera.workflows.models` - This package contains the auto-generated code that allows you to construct Argo Workflows.
  It provides Pydantic models for all the Argo Workflows OpenAPI objects, and allows you to construct workflows using
  these models. These models are based on the OpenAPI specification, and are therefore exactly the same as the models
  used by Argo Workflows.

- `hera.workflows` - This package contains the hand-written code that allows you to construct and submit Argo Workflows.
  It wraps the auto-generated code, and provides a more intuitive interface to the Argo API. It also provides a number
  of useful features, such as the ability to submit workflows from a Python function. This package has various extension
  points that allow you to plug-in the auto-generated models in case you need to use a feature that is not yet supported
  by the hand-written code.

The major differences between v4 and v5 are:

- The `hera.workflows.models` package is now auto-generated, and is based on the OpenAPI specification of Argo
  Workflows. This means that all the models are exactly the same as the models used by Argo Workflows, and you can use
  all the features of Argo Workflows in your workflows written with `hera`.

- The auto-generated models are based on Pydantic, which means that you can use all the features of Pydantic to
  construct your workflows. This includes better type-checking, auto-completion in IDEs and more.

- All template types are now supported. This means that you can now use all the template types that are supported by
  Argo Workflows, such as DAGs, Steps, Suspend and more. Previously, only the DAG template type was supported.

- The hand-written code has been rewritten to be extensible. This means that you can now easily extend the library to
  support new features, or to support features that are not yet supported by the hand-written code. This is done by
  using the `hera.workflows.models` package, and plugging it into the `hera.workflows` package.
