# K8S Owner Reference

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/k8s-owner-reference.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Resource, Workflow

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        annotations={
            "workflows.argoproj.io/description": "This example creates a Kubernetes resource that will be deleted\nwhen the workflow is deleted via Kubernetes GC.\n\nA workflow is used for this example, but the same approach would apply\nto other resource types.\n\nhttps://kubernetes.io/docs/concepts/workloads/controllers/garbage-collection/\n"
        },
        generate_name="k8s-owner-reference-",
        labels={"workflows.argoproj.io/test": "true"},
        entrypoint="main",
    ) as w:
        Resource(
            name="main",
            action="create",
            manifest="apiVersion: argoproj.io/v1alpha1\nkind: Workflow\nmetadata:\n  generateName: owned-eg-\nspec:\n  entrypoint: main\n  templates:\n    - name: main\n      container:\n        image: argoproj/argosay:v2",
            set_owner_reference=True,
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: k8s-owner-reference-
      annotations:
        workflows.argoproj.io/description: |
          This example creates a Kubernetes resource that will be deleted
          when the workflow is deleted via Kubernetes GC.

          A workflow is used for this example, but the same approach would apply
          to other resource types.

          https://kubernetes.io/docs/concepts/workloads/controllers/garbage-collection/
      labels:
        workflows.argoproj.io/test: 'true'
    spec:
      entrypoint: main
      templates:
      - name: main
        resource:
          action: create
          manifest: |-
            apiVersion: argoproj.io/v1alpha1
            kind: Workflow
            metadata:
              generateName: owned-eg-
            spec:
              entrypoint: main
              templates:
                - name: main
                  container:
                    image: argoproj/argosay:v2
          setOwnerReference: true
    ```

