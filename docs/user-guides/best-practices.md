# Best Practices

## Inline vs Runner Scripts

[Runner scripts](script-constructors.md#runner-scripts) have a stronger feature set than inline scripts so are the
recommended path. You will likely need to set up a CICD solution as the iterative development process can be cumbersome.
Read more in [Iterating on a Workflow](#iterating-on-a-workflow) and [CICD](#cicd).

## How To Write Workflows

### Laying Out Your Python Code

Hera aims to keep orchestration code outside of your business logic, meaning you should write business logic in
functions decorated with `@script`, and construct your Workflow separately, as seen throughout the examples. This might
involve putting code in different submodules in your application, but overall you are free to write your Workflow how
you want.

An example directory structure for a project using `poetry` might be:

```console
.
├── Dockerfile
├── hera_scratch
│   ├── __main__.py
│   └── workflow.py
├── Makefile
├── poetry.lock
├── pyproject.toml
├── README.md
└── requirements.txt
```

In this project, we use:

* a `Dockerfile` to create an image for the runner script, using the packages in `requirements.txt` and a command
  contained in the `Makefile`
* a `__main__.py` file to run the Workflow from `workflow.py` on Argo Workflows
* standard poetry/Python files

See this layout in the [example Hera project repo](https://github.com/elliotgunton/hera-example-project)!

### Steps vs DAGs

* Use Steps for simple, sequential processing
* Use DAGs to run as many tasks in parallel as possible, and if you want to only describe dependencies, not ordering

### Iterating on a Workflow

The developer process of iterating on a Workflow can be cumbersome as Argo does not offer a way to "dry run" your
Workflow, and developers often get caught out by simple errors (such as unresolved variables).

Hera should help reduce the number of iterations you need on the Workflow itself, but first you should create your
business logic in isolation, and test it as normal Python (if you are using Python). The Workflow should then be written
with the intention to test the plumbing between steps on a live Argo Workflows installation. You should have easily
"mockable" business logic, in the sense that if your Workflow will process millions of rows of data, try running the
Workflow with just a few rows at first. You can then iteratively build the Workflow from start to finish, testing the
Workflow regularly on the live cluster.

To summarise:

1. Write business logic (and tests!)
1. Add script decorators
1. Write your Workflow
1. Test as you go!

## Workflows vs WorkflowTemplates vs ClusterWorkflowTemplates

WorkflowTemplates are intended to be collections of templates that live in your Kubernetes namespace and used by other
Workflows. ClusterWorkflowTemplates are the same but are accessible from all Kubernetes namespaces, so should perform
common actions like email or Slack alerts, as they will be accessible by teams across your organisation. For brevity
throughout the docs, when we refer to "WorkflowTemplates" we are also referring to "ClusterWorkflowTemplates".

In Hera, you will usually be writing Workflows, unless you find a common pattern or template usage, which can then be
extracted into a WorkflowTemplate.

### Python Function Libraries vs WorkflowTemplates

In Hera, WorkflowTemplates seem redundant when we can build and distribute Python libaries, meaning we can distribute
script-decorated functions in versioned packages. Therefore there is not much difference to a Python end user between a
versioned WorkflowTemplates approach, and using plain old Python packages:

* For WorkflowTemplates:
    * end users will need to use `TemplateRef`
    * they only tell what the inputs should be from documentation or by looking at the YAML on the cluster (or on their
      chosen code versioning tool, e.g. GitHub)
    * you will need a custom mechanism to notify users of and distribute a new WorkflowTemplate version

* For Python packages:
    * end users should import the function and call it under a `Workflow` context
    * they can see the inputs in their IDE
    * new versions can be upgraded through common dependency auto-updaters, or manually through `pip` or `poetry`

However, if you do not create WorkflowTemplates, anyone not using Python will not be able to use your functions!

### Versioning

As Workflows and WorkflowTemplates are Custom Resource Definitions (CRDs) on Kubernetes, they can be updated in-place.
This means if you have changed a template within a WorkflowTemplate, and `apply` it on the cluster, you will change the
template for anyone who uses it in future but was expecting the previous version.

Explicitly versioning WorkflowTemplates can avoid this issue, but is not natively supported in Argo Workflows. We can
create a reasonable workaround in Hera by leveraging Python package versioning.

We can simply include the Python package's version in the WorkflowTemplate name, which keeps the Python version and
WorkflowTemplate version in sync:

```python
import my_package

VERSION = my_package.__version__
global_config.image = f"my-package:v{VERSION}"

with WorkflowTemplate(name=f"my-package-wt-v{VERSION}") as w:
    ...
```

This also allows you to create "pre-releases" of WorkflowTemplates, letting you test them out privately before releasing
them (as ClusterWorkflowTemplates).

### CICD

Following on from [Versioning](#versioning), we will need good Continuous Integration (CI) to test and Continuous
Deployment (CD) to deploy these versioned WorkflowTemplates.

### End-to-End Workflow Testing

For an end-to-end test in our CI, we'll need to build the Python image if using runner scripts, ensure all the Script
Templates use the new Python image, and then run the WorkflowTemplate as a Workflow. This can be achieved using an
environment variable from the CI tool, for example, we can run the following couple of lines from a shell:

```console
IMAGE_NAME=my-package-image-test
python -m my_package.run_test_workflow
```

Then, if we assume the WorkflowTemplate object can be imported from `my_package`, then the `run_test_workflow.py` file
might look like:

```python
VERSION = my_package.__version__
global_config.image = os.environ .get("IMAGE_NAME", f"my-package:v{VERSION}")

from my_package import workflow_template

workflow_template.create_as_workflow(generate_name="my-package-wt-test")
```

### WorkflowTemplate Deployment

If you don't have a dedicated GitOps CD tool like [Argo CD](https://argo-cd.readthedocs.io/en/stable/) (which is
recommended), your CI can run a deployment step.

For example, the following could be in a `deploy_workflow_template.py` file which runs in CI:

```python
import my_package

VERSION = my_package.__version__
global_config.image = f"my-package:v{VERSION}"

with WorkflowTemplate(name=f"my-package-wt-v{VERSION}") as w:
    ...

w.create()
```
