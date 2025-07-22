from hera.workflows import Resource, Workflow
from hera.workflows.models import Outputs, Parameter, ValueFrom

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    name="k8s-jobs",
    entrypoint="rand-num",
) as w:
    Resource(
        name="rand-num",
        outputs=Outputs(
            parameters=[
                Parameter(
                    name="job-name",
                    value_from=ValueFrom(
                        json_path="{.metadata.name}",
                    ),
                ),
                Parameter(
                    name="job-obj",
                    value_from=ValueFrom(
                        jq_filter=".",
                    ),
                ),
            ],
        ),
        action="create",
        failure_condition="status.failed > 1",
        manifest='apiVersion: batch/v1\nkind: Job\nmetadata:\n  generateName: rand-num-\nspec:\n  completions: 3\n  parallelism: 3\n  template:\n    metadata:\n      name: rand\n    spec:\n      containers:\n      - name: rand\n        image: python:alpine3.6\n        command: ["python", "-c", "import random; import time; print(random.randint(1, 1000)); time.sleep(10)"]\n      restartPolicy: Never\n',
        set_owner_reference=True,
        success_condition="status.succeeded > 2",
    )
