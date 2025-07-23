# K8S Jobs

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/k8s-jobs.yaml).




=== "Hera"

    ```python linenums="1"
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
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      name: k8s-jobs
    spec:
      entrypoint: rand-num
      templates:
      - name: rand-num
        outputs:
          parameters:
          - name: job-name
            valueFrom:
              jsonPath: '{.metadata.name}'
          - name: job-obj
            valueFrom:
              jqFilter: .
        resource:
          action: create
          failureCondition: status.failed > 1
          manifest: |
            apiVersion: batch/v1
            kind: Job
            metadata:
              generateName: rand-num-
            spec:
              completions: 3
              parallelism: 3
              template:
                metadata:
                  name: rand
                spec:
                  containers:
                  - name: rand
                    image: python:alpine3.6
                    command: ["python", "-c", "import random; import time; print(random.randint(1, 1000)); time.sleep(10)"]
                  restartPolicy: Never
          setOwnerReference: true
          successCondition: status.succeeded > 2
    ```

