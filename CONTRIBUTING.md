# Contributing to Hera

**Thank you for considering a contribution to Hera!**

Your time is the ultimate currency, and the community highly appreciates your willingness to dedicate some time to Hera
for the benefit of everyone! Remember to star the repo on GitHub and share Hera with your colleagues to grow our community!

[![Contributors](https://img.shields.io/github/contributors/argoproj-labs/hera)](https://github.com/argoproj-labs/hera)
[![Stars](https://img.shields.io/github/stars/argoproj-labs/hera)](https://github.com/argoproj-labs/hera)
[![Last commit](https://img.shields.io/github/last-commit/argoproj-labs/hera)](https://github.com/argoproj-labs/hera)

## Setting up

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

## Contributing checklist

Please keep in mind the following guidelines and practices when contributing to Hera:

1. Your commit must be signed. Hera uses [an application](https://github.com/apps/dco) that enforces the Developer 
   Certificate of Origin (DCO). Currently, a Contributor License Agreement 
   ([CLA](https://github.com/cla-assistant/cla-assistant)) check also appears on submitted pull requests. This can be
   safely ignored and is **not** a requirement for contributions to hera. This is an artifact as the Argo Project is slowly migrating projects from CLA to DCO.
1. Use `make format` to format the repository code. `make format` maps to a usage of
   [black](https://github.com/psf/black), and the repository adheres to whatever `black` uses as its strict pep8 format.
   No questions asked!
1. Use `make lint test` to lint, run tests, and typecheck on the project.
1. Add unit tests for any new code you write.
1. Add an example, or extend an existing example, with any new features you may add. Use `make examples` to ensure that the documentation and examples are in sync.

## Adding new Workflow tests

Hera has an automated-test harness that is coupled with our documentation. In order to add new tests, please follow these steps - 

### Local Hera examples

Tests that do not correspond to any upstream Argo Workflow examples should live in `examples/workflows/*.py`

In order to add a new workflow test to test Hera functionality, do the following - 
- Create a new file under `examples/workflows`, for example - `my_test.py`
- Define your new workflow. Make sure that the target workflow you wish to export and test against is named `w`
- Run tests using `make test`. Hera tests will generate a golden copy of the output YAML with the name `my-test.yaml` if it does not exist already
- If you would like to update the golden copy of the test files, you can run `make regenerate-test-data`
- The golden copies must be checked in to ensure that regressions may be caught in the future

### Upstream Hera examples

Tests that correspond to any [upstream Argo Workflow examples](https://github.com/argoproj/argo-workflows/tree/master/examples) should live in `examples/workflows/upstream/*.py`. These tests exist to ensure that Hera has complete parity with Argo Workflows and also to catch any regressions that might happen.

In order to add a new workflow test to test Hera functionality, do the following - 
- Create a new file under `examples/workflows/upstream` that corresponds with the name of the upstream example yaml file. If the yaml file has a hyphen, your python file name should replace those with an underscore. eg. if you are trying to replicate [archive-location.yaml](https://github.com/argoproj/argo-workflows/blob/master/examples/archive-location.yaml) your python file should be called `archive_location.py`
- Define your new workflow. Make sure that the target workflow you wish to export and test against is named `w`
- Run tests using `make test`. Hera tests will generate a golden copy of the output YAML with the name `archive-location.yaml` and also generate a local copy of the upstream yaml file with the name `archive-location.upstream.yaml` 
- If you would like to update the golden copy of the test files, you can run `make regenerate-test-data`
- The golden copies must be checked in to ensure that regressions may be caught in the future

## Working in VSCode

If your preferred IDE is VSCode, you may have an issue using the integrated Testing extension where breakpoints are not
respected. To solve this, add the following as a config in your `.vscode/launch.json` file:

```json
{
   "name": "Debug Tests",
   "type": "python",
   "request": "launch",
   "purpose": ["debug-test"],
   "console": "integratedTerminal",
   "justMyCode": false,
   "env": {"PYTEST_ADDOPTS": "--no-cov"}
}
```

## Code of Conduct

Please be mindful of and adhere to the CNCF's
[Code of Conduct](https://github.com/cncf/foundation/blob/main/code-of-conduct.md) when contributing to hera.
