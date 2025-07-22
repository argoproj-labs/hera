from hera.workflows import Resource, Workflow

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    annotations={
        "workflows.argoproj.io/description": "This example shows a standard patch with the default mergeStrategy (strategic)\n"
    },
    generate_name="k8s-patch-pod-",
    labels={"workflows.argoproj.io/test": "true"},
    entrypoint="main",
) as w:
    Resource(
        name="main",
        action="patch",
        manifest="apiVersion: v1\nkind: Pod\nmetadata:\n  name: {{pod.name}}\n  annotations:\n    foo: bar\n",
    )
