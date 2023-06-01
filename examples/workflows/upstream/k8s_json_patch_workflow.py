from hera.workflows import Resource, Workflow

manifest = """- op: add
  path: /metadata/labels/foo
  value: bar
"""

with Workflow(
    generate_name="k8s-patch-workflow-",
    entrypoint="main",
) as w:
    Resource(
        name="main",
        action="patch",
        merge_strategy="json",
        flags=["workflow", "{{workflow.name}}"],
        manifest=manifest,
    )
