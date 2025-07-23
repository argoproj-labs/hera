# K8S Wait Wf

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/k8s-wait-wf.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Resource, Step, Steps, Workflow
    from hera.workflows.models import Arguments, Inputs, Outputs, Parameter, ValueFrom

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="k8s-wait-wf-",
        entrypoint="k8s-wait-wf",
    ) as w:
        with Steps(
            name="k8s-wait-wf",
        ) as invocator:
            Step(
                name="create-wf",
                template="create-wf",
            )
            Step(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="wf-name",
                            value="{{steps.create-wf.outputs.parameters.wf-name}}",
                        )
                    ],
                ),
                name="wait-wf",
                template="wait-wf",
            )
        Resource(
            name="create-wf",
            outputs=Outputs(
                parameters=[
                    Parameter(
                        name="wf-name",
                        value_from=ValueFrom(
                            json_path="{.metadata.name}",
                        ),
                    )
                ],
            ),
            action="create",
            manifest='apiVersion: argoproj.io/v1alpha1\nkind: Workflow\nmetadata:\n  generateName: sleep-\nspec:\n  entrypoint: sleep\n  templates:\n  - name: sleep\n    container:\n      image: alpine:latest\n      command: [sleep, "20"]\n',
        )
        Resource(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="wf-name",
                    )
                ],
            ),
            name="wait-wf",
            action="get",
            failure_condition="status.phase in (Failed, Error)",
            manifest="apiVersion: argoproj.io/v1alpha1\nkind: Workflow\nmetadata:\n  name: {{inputs.parameters.wf-name}}\n",
            success_condition="status.phase == Succeeded",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: k8s-wait-wf-
    spec:
      entrypoint: k8s-wait-wf
      templates:
      - name: k8s-wait-wf
        steps:
        - - name: create-wf
            template: create-wf
        - - name: wait-wf
            template: wait-wf
            arguments:
              parameters:
              - name: wf-name
                value: '{{steps.create-wf.outputs.parameters.wf-name}}'
      - name: create-wf
        outputs:
          parameters:
          - name: wf-name
            valueFrom:
              jsonPath: '{.metadata.name}'
        resource:
          action: create
          manifest: |
            apiVersion: argoproj.io/v1alpha1
            kind: Workflow
            metadata:
              generateName: sleep-
            spec:
              entrypoint: sleep
              templates:
              - name: sleep
                container:
                  image: alpine:latest
                  command: [sleep, "20"]
      - name: wait-wf
        inputs:
          parameters:
          - name: wf-name
        resource:
          action: get
          failureCondition: status.phase in (Failed, Error)
          manifest: |
            apiVersion: argoproj.io/v1alpha1
            kind: Workflow
            metadata:
              name: {{inputs.parameters.wf-name}}
          successCondition: status.phase == Succeeded
    ```

