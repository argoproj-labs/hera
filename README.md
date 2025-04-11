# Hera

| <img src="https://raw.githubusercontent.com/argoproj-labs/hera/main/docs/assets/hera-logo.svg" alt="Hera mascot"> | Hera is the go-to Python SDK to make Argo Workflows simple and intuitive. Easily turn Python functions into containerised templates that run on Kubernetes, with full access to its capabilities. |
|---|---|

[See the Quick Start guide](https://hera.readthedocs.io/en/stable/walk-through/quick-start/) to start using Hera to
orchestrate your Argo Workflows!

```text
The Argo was constructed by the shipwright Argus,
and its crew were specially protected by the goddess Hera.
```

### PyPI stats

[![PyPI](https://img.shields.io/pypi/v/hera.svg)](https://pypi.python.org/pypi/hera)
[![Versions](https://img.shields.io/pypi/pyversions/hera.svg)](https://github.com/argoproj-labs/hera)

[![Downloads](https://static.pepy.tech/badge/hera)](https://pepy.tech/project/hera)
[![Downloads/month](https://static.pepy.tech/badge/hera/month)](https://pepy.tech/project/hera)
[![Downloads/week](https://static.pepy.tech/badge/hera/week)](https://pepy.tech/project/hera)

### Repo information

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/license/apache-2-0/)
[![CICD](https://github.com/argoproj-labs/hera/actions/workflows/cicd.yaml/badge.svg)](https://github.com/argoproj-labs/hera/actions/workflows/cicd.yaml)
[![Docs](https://readthedocs.org/projects/hera/badge/?version=latest)](https://hera.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/argoproj-labs/hera/branch/main/graph/badge.svg?token=x4tvsQRKXP)](https://codecov.io/gh/argoproj-labs/hera)

## Hera at a glance

```python
from hera.workflows import DAG, Workflow, script


# Turn a function into a reusable "Script template"
# using the script decorator
@script()
def echo(message: str):
    print(message)


# Orchestration logic lives *outside* of business logic
with Workflow(
    generate_name="dag-diamond-",
    entrypoint="diamond",
) as w:
    with DAG(name="diamond"):
        A = echo(name="A", arguments={"message": "A"})
        B = echo(name="B", arguments={"message": "B"})
        C = echo(name="C", arguments={"message": "C"})
        D = echo(name="D", arguments={"message": "D"})
        A >> [B, C] >> D  # Define execution order

# Create the workflow directly on your Argo Workflows cluster!
w.create()
```

Check out the [examples](./examples/workflows-examples.md) to see how to construct and submit Argo Workflows with Hera!

## Requirements

Hera requires an Argo Workflows server to be deployed to a Kubernetes cluster. To learn how to deploy Argo to your own
Kubernetes cluster you can follow the [Argo Workflows](https://argoproj.github.io/argo-workflows/quick-start/) guide!

### Authenticating in Hera

Hera assumes that the Argo server sits behind an authentication layer, so workflow submission requests are authenticated
using a Bearer token on the request. Another option for workflow submission without the authentication layer is using
port forwarding to your Argo server deployment and submitting workflows to `localhost:2746`.

There are a few ways to authenticate in Hera - read more in the
[authentication walkthrough](https://hera.readthedocs.io/en/stable/walk-through/authentication/) - for now, with the
`argo` cli tool installed, and the server port-forwarded to `localhost:2746`, this example will get you up and running:

```py
from hera.workflows import Workflow, Container
from hera.shared import global_config
from hera.auth import ArgoCLITokenGenerator

global_config.host = "http://localhost:2746"
global_config.token = ArgoCLITokenGenerator

with Workflow(generate_name="local-test-", entrypoint="c") as w:
    Container(name="c", image="docker/whalesay", command=["cowsay", "hello"])

w.create()
```

## Installation

| Source                                               | Command                                                                                                 |
|------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| [PyPI](https://pypi.org/project/hera/)               | `pip install hera`                                                                                      |
| [GitHub repo](https://github.com/argoproj-labs/hera) | `python -m pip install git+https://github.com/argoproj-labs/hera --ignore-installed` |


### Optional dependencies

#### `yaml`

- Install via `hera[yaml]`
- [PyYAML](https://pypi.org/project/PyYAML/) is required for the `yaml` output format, which is accessible via
  `hera.workflows.Workflow.to_yaml(*args, **kwargs)`. This enables GitOps practices and easier debugging.

#### `cli`

- Install via `hera[cli]`. The `[cli]` option installs the extra dependency [Cappa](https://github.com/DanCardin/cappa)
  required for the CLI
- The CLI aims to enable GitOps practices,
  easier debugging, and a more seamless experience with Argo Workflows.
- **_The CLI is an experimental feature and subject to change!_** At the moment it only supports generating YAML files
  from workflows via `hera generate yaml`. See `hera generate yaml --help` for more information.

#### `experimental`
 - Install via `hera[experimental]`. The `[experimental]` option adds dependencies required for experimental features that have not yet graduated into stable features.

## Presentations

<!-- Add 3 most recent talks here. Keep in sync with docs homepage (docs/index.md). -->

- [KubeCon/ArgoCon EU 2025 - One Engine To Rule Them All: Unifying Cloud Workloads With Argo Workflows](https://www.youtube.com/watch?v=Xpo5218Ark8&list=PLj6h78yzYM2N9MWCsU_4upn64NDtHGv6i&index=18)
- [KubeCon/ArgoCon NA 2024 - Data Science Workflows Made Easy: Python-Powered Argo for Your Organization](https://www.youtube.com/watch?v=hZOcj5uVQOo&list=PLj6h78yzYM2Ow7Jy0paxwrimeuFGONU_7&index=14)
- [KubeCon/ArgoCon EU 2024 - Orchestrating Python Functions Natively in Argo Using Hera](https://www.youtube.com/watch?v=4G3Q6VMBvfI&list=PLj6h78yzYM2NA4NbSC6_mQNza2r3WV87h&index=4)

<details><summary><i>More presentations</i></summary>

- [CNCF TAG App-Delivery @ KubeCon NA 2023 - Automating the Deployment of Data Workloads to Kubernetes with ArgoCD, Argo Workflows, and Hera](https://www.youtube.com/watch?v=NZCmYRVziGY&t=12481s&ab_channel=CNCFTAGAppDelivery)
- [KubeCon/ArgoCon NA 2023 - How to Train an LLM with Argo Workflows and Hera](https://www.youtube.com/watch?v=nRYf3GkKpss&ab_channel=CNCF%5BCloudNativeComputingFoundation%5D)
    - [Featured code](https://github.com/flaviuvadan/kubecon_na_23_llama2_finetune)
- [KubeCon/ArgoCon EU 2023 - Scaling gene therapy with Argo Workflows and Hera](https://www.youtube.com/watch?v=h2TEw8kd1Ds)
- [DoKC Town Hall #2 - Unsticking ourselves from Glue - Migrating PayIt's Data Pipelines to Argo Workflows and Hera](https://youtu.be/sSLFVIIEKcE?t=2088)
- [Argo Workflows and Events Community Meeting 15 June 2022 - Hera project update](https://youtu.be/sdkBDPOdQ-g?t=231)
- [Argo Workflows and Events Community Meeting 20 Oct 2021 - Hera introductory presentation](https://youtu.be/QETfzfVV-GY?t=181)

</details>

## Blogs

<!-- Add 3 most recent blogs here. Keep in sync with docs homepage (docs/index.md). -->

- [Hera Developer Survey 2025](https://dev.to/elliot_gunton_73028975583/hera-developer-survey-2025-168d)
- [How To Get the Most out of Hera for Data Science](https://pipekit.io/blog/how-to-get-the-most-out-of-hera-for-data-science)
- [Data Validation with Great Expectations and Argo Workflows](https://towardsdatascience.com/data-validation-with-great-expectations-and-argo-workflows-b8e3e2da2fcc)

<details><summary><i>More blogs</i></summary>

- [Hera introduction and motivation](https://www.dynotx.com/hera-the-missing-argo-workflows-python-sdk/)
- [Dyno is scaling gene therapy research with cloud-native tools like Argo Workflows and Hera](https://www.dynotx.com/argo-workflows-hera/)

</details>

## Contributing

Use one of the following to open the repo in a cloud dev box:

<a href="https://codespaces.new/argoproj-labs/hera"><img src=https://github.com/codespaces/badge.svg height="32" alt="Open in GitHub Codespaces"></a>
<a href="https://gitpod.io/#https://github.com/argoproj-labs/hera"><img src=https://gitpod.io/button/open-in-gitpod.svg height="32" alt="Open in Gitpod"></a>

Read more in the [contributing guide](./CONTRIBUTING.md)!

## Hera Emeritus Maintainers

These emeritus maintainers dedicated a part of their career to Hera and reviewed code, triaged bugs and pushed the
project forward over a substantial period of time. Their contribution is greatly appreciated:

- [Flaviu Vadan](https://github.com/flaviuvadan)

## License

Hera is licensed under Apache 2.0. See [License](https://github.com/argoproj-labs/hera/blob/main/LICENSE) for details.
