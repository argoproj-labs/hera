# K8S Patch Pod

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/k8s-patch-pod.yaml).




=== "Hera"

    ```python linenums="1"
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
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: k8s-patch-pod-
      annotations:
        workflows.argoproj.io/description: |
          This example shows a standard patch with the default mergeStrategy (strategic)
      labels:
        workflows.argoproj.io/test: 'true'
    spec:
      entrypoint: main
      templates:
      - name: main
        resource:
          action: patch
          manifest: |
            apiVersion: v1
            kind: Pod
            metadata:
              name: {{pod.name}}
              annotations:
                foo: bar
    ```

