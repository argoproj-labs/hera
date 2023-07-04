# K8S Json Patch Workflow

> Note: This example is a replication of an Argo Workflow example in Hera. 




=== "Hera"

    ```python linenums="1"
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
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: k8s-patch-workflow-
    spec:
      entrypoint: main
      templates:
      - name: main
        resource:
          action: patch
          flags:
          - workflow
          - '{{workflow.name}}'
          manifest: "- op: add\n  path: /metadata/labels/foo\n  value: bar\n"
          mergeStrategy: json
    ```

