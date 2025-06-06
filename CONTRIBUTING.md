# Contributing to Hera

**Thank you for considering a contribution to Hera!**

Your time is the ultimate currency, and the community highly appreciates your willingness to dedicate some time to Hera
for the benefit of everyone! Remember to star the repo on GitHub and share Hera with your colleagues to grow our community!

[![Contributors](https://img.shields.io/github/contributors/argoproj-labs/hera)](https://github.com/argoproj-labs/hera)
[![Stars](https://img.shields.io/github/stars/argoproj-labs/hera)](https://github.com/argoproj-labs/hera/stargazers)
[![Last commit](https://img.shields.io/github/last-commit/argoproj-labs/hera)](https://github.com/argoproj-labs/hera)

## New Contributor Guide

We welcome code contributions for new features and bug fixes that address
issues labeled with ["good-first-issue"](https://github.com/argoproj-labs/hera/issues?q=is%3Aopen+is%3Aissue+label%3Anote%3Agood-first-issue)
or
["ideal-for-contribution"](https://github.com/argoproj-labs/hera/issues?q=is%3Aopen+is%3Aissue+label%3Anote%3Aideal-for-contribution).

We also encourage contributions in the form of:

* Adding your organization as a [user of Hera](https://github.com/argoproj-labs/hera/blob/main/USERS.md)!
* Answering questions on [GitHub Discussions](https://github.com/argoproj-labs/hera/discussions) and
  [Slack](https://cloud-native.slack.com/archives/C03NRMD9KPY)
* Blog Posts / Social Media featuring Hera
* Attending the Hera [working group meeting](https://bloomberg.zoom.us/j/98693513976?pwd=QXVDRkFCZ1FybkIwdkdsWWdFa3NWUT09) (bi-weekly on Fridays, 3pm GMT / 3pm BST)
  * Add notes to our [community agenda doc](https://docs.google.com/document/d/1IpHkxsxWdE0lhgpDj_pXYGotsa3s38koCzawlHyH860/edit) for the meeting

If you have an idea for a large feature, please reach out to us on the Slack channel or attend the working group
meetings first, and then we can help you propose the feature using
[the CNCF design proposal template](https://github.com/cncf/project-template/blob/main/DESIGN-PROPOSALS.md?plain=1).

### Setting up

If you plan to submit contributions to Hera, you will need the `make` and `poetry` CLI tools. Poetry manages Python
virtual environments - see the [Poetry Installation guide](https://python-poetry.org/docs/#installation) to install with
`pipx` or the Poetry installer. Make is used to set useful aliases as `make` targets. You should first install Hera's
dependencies via the `make install` target which will create a virtual environment using the version of Python used on
your system:

```shell
make install
```

Once the dependencies are installed, you can use the various `make` targets to replicate the `CI` jobs, starting with
`make ci` to run all tests and linting checks.

You can view the available `make` targets via `make help` or just `make`.

```
make help
build-docs                     Generate documentation locally
check-codegen                  Check if the code is up to date
ci                             Run all the CI checks
codegen                        Generate all models, services, examples, and init files
events-models                  Generate the Events models portion of Argo Workflows
events-service                 Generate the events service option of Hera
examples                       Generate documentation files for examples
fetch-upstream-examples        Fetch the upstream examples, add missing examples report to docs
format                         Format and sort imports for source, tests, examples, etc.
help                           Showcase the help instructions for all the available `make` commands
host-docs                      Host and open the documentation locally (and rebuild automatically)
init-files                     Generate the init-files of Hera
install-argo                   Install argo CLI client
install                        Run poetry install with all extras for development
lint                           Run a `lint` process on Hera and report problems
models                         Generate all the Argo Workflows models
regenerate-example             Regenerates the yaml for a single example, using EXAMPLE_FILENAME envvar
regenerate-test-data           Regenerates test data and docs for non-upstream examples
regenerate-upstream-test-data  Regenerates test data and docs for upstream examples
services                       Generate the services of Hera
set-up-argo                    Start the argo service
set-up-artifacts               Adds minio for running examples with artifact storage
set-up-cluster                 Create the cluster and argo namespace
stop-cluster                   Stop the cluster
test-on-cluster                Run workflow tests (requires local argo cluster)
test-type-hints                Run type hint tests for Hera
test                           Run tests for Hera
workflows-models               Generate the Workflows models portion of Argo Workflows
workflows-service              Generate the Workflows service option of Hera
```

#### Installing Argo Workflows in GitHub Codespaces

You can install Argo and try running Hera code in GitHub Codespaces. First, open the Hera repository in Codespaces using the link below:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new/argoproj-labs/hera)

Then, you can run the `make` commands to install k3d (a lightweight Kubernetes CLI), and then install the Argo Workflows controller on the cluster:

```
make install-k3d run-argo
```

You can [take a look at `test_submission.py`](https://github.com/argoproj-labs/hera/blob/ec06876f1abc0d3309b000f3cd2e0eca64891da9/tests/test_submission.py) to see how to submit a Workflow using Hera and write your own. You can run the test Workflow using:

```
make test-on-cluster
```

See the [Viewing the Argo UI from a Codespace](#viewing-the-argo-ui-from-a-codespace) guide to see the Workflow in the UI.

Otherwise you can install the Argo CLI with

```
make install-argo
```

which will then let you do things like listing the Workflows in the `argo` namespace with

```
argo list --namespace argo
```

#### Working in VSCode

If your preferred IDE is VSCode, you may have an issue using the integrated Testing extension where breakpoints are not
respected. To solve this, add the following as a config in your `.vscode/launch.json` file:

```json
{
   "name": "Debug Tests",
   "type": "debugpy", // "python" is now deprecated
   "request": "launch",
   "purpose": ["debug-test"],
   "console": "integratedTerminal",
   "justMyCode": false,
   "env": {"PYTEST_ADDOPTS": "--no-cov"}
}
```

## Contributing checklist

Please keep in mind the following guidelines and practices when contributing to Hera:

1. Your commit must be signed (`git commit --signoff`). Hera uses the [DCO application](https://github.com/apps/dco)
   that enforces the Developer Certificate of Origin (DCO) on commits.
1. Use `make format` to format the repository code. `make format` maps to a usage of
   [ruff](https://docs.astral.sh/ruff/formatter/), and the repository adheres to whatever `ruff` uses as its strict pep8
   format. No questions asked!
1. Use `make lint test` to lint, run tests, and typecheck on the project.
1. Add unit tests for any new code you write.
1. Add an example, or extend an existing example, with any new features you may add. Use `make examples` to ensure that
   the documentation and examples are in sync.

## Adding new Workflow YAML generation tests

Hera has an automated-test harness that is coupled with our documentation. In order to add new tests, please follow these steps -

### Local Hera examples

Tests that do not correspond to any upstream Argo Workflow examples should live in one of the topic folders under
`examples/workflows/`, e.g. `dags` or `loops`. Use `misc` if there isn't a specific topic that matches.

In order to add a new workflow test to test Hera functionality, do the following -

* Create a new file under `examples/workflows`, for example - `my_test.py`
* Define your new workflow. Make sure that the target workflow you wish to export and test against is named `w`
* Run tests using `make test`. Hera tests will generate a golden copy of the output YAML with the name `my-test.yaml` if
  it does not exist already
* If you would like to update the golden copy of the test files, you can run `make regenerate-test-data`
* The golden copies must be checked in to ensure that regressions may be caught in the future

### Upstream Hera examples

Tests that correspond to any
[upstream Argo Workflow examples](https://github.com/argoproj/argo-workflows/tree/main/examples) should live in
`examples/workflows/upstream/*.py`. These tests exist to ensure that Hera has complete parity with Argo Workflows and
also to catch any regressions that might happen.

In order to add a new workflow test to test Hera functionality, do the following -

* Create a new file under `examples/workflows/upstream` that corresponds with the name of the upstream example yaml
  file. If the yaml file has a hyphen, your python file name should replace those with an underscore. eg. if you are
  trying to replicate
  [archive-location.yaml](https://github.com/argoproj/argo-workflows/blob/main/examples/archive-location.yaml) your
  python file should be called `archive_location.py`
* Define your new workflow. Make sure that the target workflow you wish to export and test against is named `w`
* Run tests using `make test`. Hera tests will generate a golden copy of the output YAML with the name
  `archive-location.yaml` and also generate a local copy of the upstream yaml file with the name
  `archive-location.upstream.yaml`
* If you would like to update the golden copy of the test files, you can run `make regenerate-upstream-test-data`
* The golden copies must be checked in to ensure that regressions may be caught in the future

## Adding new Workflow on-cluster tests

Hera's CICD spins up Argo Workflows on a local Kubernetes cluster, which runs tests decorated with
`@pytest.mark.on_cluster`. If you want to add more on-cluster tests, the easiest way is through a GitHub Codespace. You
can then run the same `make` commands that run in CICD:

```
make install-k3d
```

This will install the k3d CLI.

```
make run-argo
```

This will create a cluster using k3d called `test-cluster`, then create a namespace called `argo` on it, applying the
argo configuration, and patching the deployment to use `server` as the `auth-mode`, meaning the connection to submit the
workflow doesn't require an authentication mechanism.

You can then run existing on-cluster tests to ensure everything is set up correctly. This command also ports-forward the
server's port.

```
make test-on-cluster
```

### Viewing the Argo UI from a Codespace

> Before doing this, note that **anyone** will be able to connect using the Argo UI URL!

Ensure Argo Workflows is running using the `make` command:

```
make run-argo
```

Forward the Server's port using kubectl:

```
kubectl -n argo port-forward deployment/argo-server 2746:2746
```

Then, go to the `PORTS` panel in VSCode, and add the `2746` port. You should see a green circle to the left of the port.
Then right click on the `2746` row and set `Port Visibility` to `public`. You can then open the URL in your browser to view the Argo UI.

## Code of Conduct

Please be mindful of, and adhere to, the CNCF's
[Code of Conduct](https://github.com/cncf/foundation/blob/main/code-of-conduct.md) when contributing to hera.
