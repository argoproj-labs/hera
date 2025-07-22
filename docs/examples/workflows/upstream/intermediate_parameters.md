# Intermediate Parameters

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/intermediate-parameters.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Suspend, Workflow
    from hera.workflows.models import Inputs, Outputs, Parameter, SuppliedValueFrom, ValueFrom

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="intermediate-parameters-cicd-",
        entrypoint="cicd-pipeline",
    ) as w:
        with Steps(
            name="cicd-pipeline",
        ) as invocator:
            Step(
                name="deploy-pre-prod",
                template="deploy",
            )
            Step(
                name="approval",
                template="approval",
            )
            Step(
                name="deploy-prod",
                template="deploy",
                when="{{steps.approval.outputs.parameters.approve}} == YES",
            )
        Suspend(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        default="NO",
                        description="Choose YES to continue workflow and deploy to production",
                        enum=["YES", "NO"],
                        name="approve",
                    )
                ],
            ),
            name="approval",
            outputs=Outputs(
                parameters=[
                    Parameter(
                        name="approve",
                        value_from=ValueFrom(
                            supplied=SuppliedValueFrom(),
                        ),
                    )
                ],
            ),
        )
        Container(
            name="deploy",
            args=["echo", "deploying"],
            command=["/argosay"],
            image="argoproj/argosay:v2",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: intermediate-parameters-cicd-
    spec:
      entrypoint: cicd-pipeline
      templates:
      - name: cicd-pipeline
        steps:
        - - name: deploy-pre-prod
            template: deploy
        - - name: approval
            template: approval
        - - name: deploy-prod
            template: deploy
            when: '{{steps.approval.outputs.parameters.approve}} == YES'
      - name: approval
        inputs:
          parameters:
          - name: approve
            default: 'NO'
            description: Choose YES to continue workflow and deploy to production
            enum:
            - 'YES'
            - 'NO'
        outputs:
          parameters:
          - name: approve
            valueFrom:
              supplied: {}
        suspend: {}
      - name: deploy
        container:
          image: argoproj/argosay:v2
          args:
          - echo
          - deploying
          command:
          - /argosay
    ```

