from hera.workflows import Resource, Workflow

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    annotations={
        "workflows.argoproj.io/description": "This example shows a more advanced patch with json mergeStrategy\n"
    },
    generate_name="k8s-patch-json-pod-",
    labels={"workflows.argoproj.io/test": "true"},
    entrypoint="main",
) as w:
    Resource(
        name="main",
        action="patch",
        flags=["pod", "{{pod.name}}"],
        manifest="- op: add\n  path: /metadata/annotations/foo\n  value: bar\n",
        merge_strategy="json",
    )
