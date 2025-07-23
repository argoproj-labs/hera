# K8S Patch Merge Pod

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/k8s-patch-merge-pod.yaml).




=== "Hera"

    ```python linenums="1"
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
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: k8s-patch-merge-pod-
      annotations:
        workflows.argoproj.io/description: |
          This example shows a more advanced JSON merge patch
      labels:
        workflows.argoproj.io/test: 'true'
    spec:
      entrypoint: main
      templates:
      - name: main
        resource:
          action: patch
          manifest: |
            metadata:
              annotations:
                foo: bar
          mergeStrategy: merge
          flags:
          - pod
          - '{{pod.name}}'
    ```

