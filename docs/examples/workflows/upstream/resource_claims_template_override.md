# Resource Claims Template Override

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/resource-claims-template-override.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow
    from hera.workflows.models import PodResourceClaim, ResourceClaim, ResourceRequirements

    with Workflow(
        generate_name="resource-claims-template-override-",
        labels={"workflows.argoproj.io/no-test": "environment"},
        entrypoint="main",
        resource_claims=[
            PodResourceClaim(name="accelerator", resource_claim_template_name="example-device-claim-template"),
        ],
    ) as w:
        default_device = Container(
            name="default-device",
            image="busybox",
            command=["echo"],
            args=["using the workflow default device"],
            resources=ResourceRequirements(claims=[ResourceClaim(name="accelerator")]),
        )
        other_device = Container(
            name="other-device",
            resource_claims=[
                PodResourceClaim(name="accelerator", resource_claim_template_name="example-large-device-claim-template"),
            ],
            image="busybox",
            command=["echo"],
            args=["using a different device"],
            resources=ResourceRequirements(claims=[ResourceClaim(name="accelerator")]),
        )

        with Steps(name="main"):
            Step(name="default-device", template=default_device)
            Step(name="other-device", template=other_device)
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: resource-claims-template-override-
      labels:
        workflows.argoproj.io/no-test: environment
    spec:
      entrypoint: main
      resourceClaims:
      - name: accelerator
        resourceClaimTemplateName: example-device-claim-template
      templates:
      - name: default-device
        container:
          image: busybox
          args:
          - using the workflow default device
          command:
          - echo
          resources:
            claims:
            - name: accelerator
      - name: other-device
        resourceClaims:
        - name: accelerator
          resourceClaimTemplateName: example-large-device-claim-template
        container:
          image: busybox
          args:
          - using a different device
          command:
          - echo
          resources:
            claims:
            - name: accelerator
      - name: main
        steps:
        - - name: default-device
            template: default-device
        - - name: other-device
            template: other-device
    ```

