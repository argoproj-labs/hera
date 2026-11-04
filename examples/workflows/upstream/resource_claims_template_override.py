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
