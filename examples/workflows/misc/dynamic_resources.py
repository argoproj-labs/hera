"""This example showcases how to compute dynamic resources for a step/task and pass them through.

This is useful when you write workflows in a business context that requires processing some data dynamically. For
example, if you have a step that performs QC checks on some data, and only a subset of the data passes the checks, then
you can compute the resources dynamically based on the amount of data you need to process in follow up steps.

!!! Warning
    You cannot use `resources` in the script decorator to set dynamic resources using string-templated input
    parameters, as Argo validates the value so it will fail linting.
"""

import json

from hera.workflows import DAG, Workflow, script


@script()
def compute_resources() -> None:
    """Computes the resources necessary by the following job, which could be anything."""
    import json
    import sys

    resources = []
    for i in range(1, 4):
        resources.append({"cpu": i, "mem": "{v}Mi".format(v=i * 100)})

    json.dump(resources, sys.stdout)


@script(
    pod_spec_patch=json.dumps(
        {
            "containers": [
                {
                    "name": "main",
                    "resources": {
                        "limits": {
                            "cpu": "{{inputs.parameters.cpu}}",
                            "memory": "{{inputs.parameters.mem}}",
                        },
                        "requests": {
                            "cpu": "{{inputs.parameters.cpu}}",
                            "memory": "{{inputs.parameters.mem}}",
                        },
                    },
                }
            ]
        }
    ),
)
def resource_consumer(cpu: int, mem: str) -> None:
    """Perform some computation."""
    print("received cpu {cpu} and mem {mem}".format(cpu=cpu, mem=mem))


@script(
    pod_spec_patch=json.dumps(
        {
            "containers": [
                {
                    "name": "main",
                    "resources": {
                        "limits": {
                            "cpu": "{{inputs.parameters.cpu}}",
                            "memory": "{{inputs.parameters.mem}}",
                        },
                        "requests": {
                            "cpu": "{{inputs.parameters.cpu}}",
                            "memory": "{{inputs.parameters.mem}}",
                        },
                    },
                }
            ]
        }
    ),
)
def another_resource_consumer(cpu: int = 1, mem: str = "100Mi") -> None:
    """Perform some computation."""
    print("received cpu {cpu} and mem {mem}".format(cpu=cpu, mem=mem))


with Workflow(
    generate_name="dynamic-resources-",
    entrypoint="d",
) as w:
    with DAG(name="d"):
        c = compute_resources()
        # when you don't have kwargs set for a function like `resource_consumer` then Hera can infer that you
        # likely want to map the `resource_consumer` parameters to the `with_param` output of `generate_resources`!
        # This relies on the `with_param` field, as Hera needs to know there's some dynamic input to `resource_consumer`
        c >> resource_consumer(with_param=c.result)
        # by comparison, `another_resource_consumer` has kwargs set, so Hera will not infer that you want to map
        # all of the outputs of `generate_resources` to the inputs. Instead, you are able to map the values you want,
        # and use the default value of for `mem` in the `another_resource_consumer` script template.
        c >> another_resource_consumer(
            with_param=c.result,
            arguments={"cpu": "{{item.cpu}}"},
        )
