from hera.workflows import Resource, Workflow

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    annotations={"workflows.argoproj.io/description": "This example shows a more advanced JSON merge patch\n"},
    generate_name="k8s-patch-merge-pod-",
    labels={"workflows.argoproj.io/test": "true"},
    entrypoint="main",
) as w:
    Resource(
        name="main",
        action="patch",
        flags=["pod", "{{pod.name}}"],
        manifest="metadata:\n  annotations:\n    foo: bar\n",
        merge_strategy="merge",
    )
