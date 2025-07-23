# K8S Patch Json Pod

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/k8s-patch-json-pod.yaml).




=== "Hera"

    ```python linenums="1"
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
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: k8s-patch-json-pod-
      annotations:
        workflows.argoproj.io/description: |
          This example shows a more advanced patch with json mergeStrategy
      labels:
        workflows.argoproj.io/test: 'true'
    spec:
      entrypoint: main
      templates:
      - name: main
        resource:
          action: patch
          manifest: |
            - op: add
              path: /metadata/annotations/foo
              value: bar
          mergeStrategy: json
          flags:
          - pod
          - '{{pod.name}}'
    ```

