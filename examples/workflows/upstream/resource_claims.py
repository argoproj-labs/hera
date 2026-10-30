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
