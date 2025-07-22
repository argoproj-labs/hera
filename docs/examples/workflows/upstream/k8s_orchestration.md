# K8S Orchestration

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/k8s-orchestration.yaml).




=== "Hera"

    ```python linenums="1"
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
            image="argoproj/argoexec:latest",
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
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: k8s-orchestrate-
    spec:
      entrypoint: k8s-orchestrate
      templates:
      - name: k8s-orchestrate
        steps:
        - - name: random-number-job
            template: random-number-job
        - - name: print-generated-numbers
            template: print-generated-numbers
            arguments:
              parameters:
              - name: job-uid
                value: '{{steps.random-number-job.outputs.parameters.job-uid}}'
        - - name: delete-job
            template: delete-job
            arguments:
              parameters:
              - name: job-name
                value: '{{steps.random-number-job.outputs.parameters.job-name}}'
      - name: random-number-job
        outputs:
          parameters:
          - name: job-name
            valueFrom:
              jsonPath: '{.metadata.name}'
          - name: job-uid
            valueFrom:
              jsonPath: '{.metadata.uid}'
        resource:
          action: create
          failureCondition: status.failed > 0
          manifest: |
            apiVersion: batch/v1
            kind: Job
            metadata:
              generateName: rand-num-
            spec:
              completions: 10
              parallelism: 10
              template:
                metadata:
                  name: rand
                spec:
                  containers:
                  - name: rand
                    image: python:alpine3.6
                    command: ["python", "-c", "import random; import time; print(random.randint(1, 1000)); time.sleep(10)"]
                  restartPolicy: Never
          successCondition: status.succeeded > 9
      - name: print-generated-numbers
        container:
          image: argoproj/argoexec:latest
          args:
          - ' for i in `kubectl get pods -l controller-uid={{inputs.parameters.job-uid}}
            -o name`; do kubectl logs $i; done '
          command:
          - sh
          - -c
        inputs:
          parameters:
          - name: job-uid
      - name: delete-job
        inputs:
          parameters:
          - name: job-name
        resource:
          action: delete
          manifest: |
            apiVersion: batch/v1
            kind: Job
            metadata:
              name: {{inputs.parameters.job-name}}
    ```

