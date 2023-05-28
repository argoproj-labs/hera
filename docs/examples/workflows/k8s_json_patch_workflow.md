# K8S Json Patch Workflow






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Resource, Workflow

    with Workflow(
        generate_name="k8s-patch-workflow-",
        entrypoint="main",
    ) as w:
        Resource(
            name="main",
            action="patch",
            merge_strategy="json",
            flags=["workflow", "{{workflow.name}}"],
            manifest="""
            - op: add
              path: /metadata/labels/foo
              value:bar
            """,
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
          manifest: "\n        - op: add\n          path: /metadata/labels/foo\n     \
            \     value:bar\n        "
          mergeStrategy: json
    ```

