from hera.workflows import Resource, Workflow

manifest = """apiVersion: v1
kind: ConfigMap
metadata:
  generateName: owned-eg-
data:
  some: value\n"""

with Workflow(
    generate_name="k8s-set-owner-reference-",
    entrypoint="k8s-set-owner-reference",
) as w:
    create_route = Resource(
        name="k8s-set-owner-reference",
        action="create",
        manifest=manifest,
        set_owner_reference=True,
    )
