# Resource Claims

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/resource-claims.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Workflow
    from hera.workflows.models import PodResourceClaim, ResourceClaim, ResourceRequirements

    with Workflow(
        generate_name="resource-claims-",
        labels={"workflows.argoproj.io/no-test": "environment"},
        entrypoint="show-devices",
        resource_claims=[
            PodResourceClaim(name="accelerator", resource_claim_template_name="example-device-claim-template"),
        ],
    ) as w:
        Container(
            name="show-devices",
            image="busybox",
            command=["sh", "-c"],
            args=["echo using the allocated device"],
            resources=ResourceRequirements(claims=[ResourceClaim(name="accelerator")]),
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: resource-claims-
      labels:
        workflows.argoproj.io/no-test: environment
    spec:
      entrypoint: show-devices
      resourceClaims:
      - name: accelerator
        resourceClaimTemplateName: example-device-claim-template
      templates:
      - name: show-devices
        container:
          image: busybox
          args:
          - echo using the allocated device
          command:
          - sh
          - -c
          resources:
            claims:
            - name: accelerator
    ```

