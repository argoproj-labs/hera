from hera.workflows import Resource, Workflow

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    annotations={
        "workflows.argoproj.io/description": "This example creates a Kubernetes resource that will be deleted\nwhen the workflow is deleted via Kubernetes GC.\n\nA workflow is used for this example, but the same approach would apply\nto other resource types.\n\nhttps://kubernetes.io/docs/concepts/workloads/controllers/garbage-collection/\n"
    },
    generate_name="k8s-owner-reference-",
    labels={"workflows.argoproj.io/test": "true"},
    entrypoint="main",
) as w:
    Resource(
        name="main",
        action="create",
        manifest="apiVersion: argoproj.io/v1alpha1\nkind: Workflow\nmetadata:\n  generateName: owned-eg-\nspec:\n  entrypoint: main\n  templates:\n    - name: main\n      container:\n        image: argoproj/argosay:v2",
        set_owner_reference=True,
    )
