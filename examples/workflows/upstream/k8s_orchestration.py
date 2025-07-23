from hera.workflows import Container, Resource, Step, Steps, Workflow
from hera.workflows.models import Arguments, Inputs, Outputs, Parameter, ValueFrom

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="k8s-orchestrate-",
    entrypoint="k8s-orchestrate",
) as w:
    with Steps(
        name="k8s-orchestrate",
    ) as invocator:
        Step(
            name="random-number-job",
            template="random-number-job",
        )
        Step(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="job-uid",
                        value="{{steps.random-number-job.outputs.parameters.job-uid}}",
                    )
                ],
            ),
            name="print-generated-numbers",
            template="print-generated-numbers",
        )
        Step(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="job-name",
                        value="{{steps.random-number-job.outputs.parameters.job-name}}",
                    )
                ],
            ),
            name="delete-job",
            template="delete-job",
        )
    Resource(
        name="random-number-job",
        outputs=Outputs(
            parameters=[
                Parameter(
                    name="job-name",
                    value_from=ValueFrom(
                        json_path="{.metadata.name}",
                    ),
                ),
                Parameter(
                    name="job-uid",
                    value_from=ValueFrom(
                        json_path="{.metadata.uid}",
                    ),
                ),
            ],
        ),
        action="create",
        failure_condition="status.failed > 0",
        manifest='apiVersion: batch/v1\nkind: Job\nmetadata:\n  generateName: rand-num-\nspec:\n  completions: 10\n  parallelism: 10\n  template:\n    metadata:\n      name: rand\n    spec:\n      containers:\n      - name: rand\n        image: python:alpine3.6\n        command: ["python", "-c", "import random; import time; print(random.randint(1, 1000)); time.sleep(10)"]\n      restartPolicy: Never\n',
        success_condition="status.succeeded > 9",
    )
    Container(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="job-uid",
                )
            ],
        ),
        name="print-generated-numbers",
        args=[
            " for i in `kubectl get pods -l controller-uid={{inputs.parameters.job-uid}} -o name`; do kubectl logs $i; done "
        ],
        command=["sh", "-c"],
        image="quay.io/argoproj/argoexec:latest",
    )
    Resource(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="job-name",
                )
            ],
        ),
        name="delete-job",
        action="delete",
        manifest="apiVersion: batch/v1\nkind: Job\nmetadata:\n  name: {{inputs.parameters.job-name}}\n",
    )
