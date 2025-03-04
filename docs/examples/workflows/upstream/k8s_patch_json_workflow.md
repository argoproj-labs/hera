# K8S Patch Json Workflow

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/k8s-patch-json-workflow.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Resource, Workflow

    manifest = """- op: add
      path: /metadata/labels/foo
      value: bar
    """

    with Workflow(
        generate_name="k8s-patch-json-workflow-",
        entrypoint="main",
    ) as w:
        Resource(
            name="main",
            action="patch",
            merge_strategy="json",
            flags=["workflow", "{{workflow.name}}"],
            manifest=manifest,
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: k8s-patch-json-workflow-
    spec:
      entrypoint: main
      templates:
      - name: main
        resource:
          action: patch
          manifest: |
            - op: add
              path: /metadata/labels/foo
              value: bar
          mergeStrategy: json
          flags:
          - workflow
          - '{{workflow.name}}'
    ```

