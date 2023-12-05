# K8S Set Owner Reference

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/k8s-set-owner-reference.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Resource, Workflow

    manifest = """apiVersion: v1
    kind: ConfigMap
    metadata:
      generateName: owned-eg-
    data:
      some: value\n"""

    with Workflow(
        generate_name="k8s-set-owner-reference-",
        entrypoint="k8s-set-owner-reference",
    ) as w:
        create_route = Resource(
            name="k8s-set-owner-reference",
            action="create",
            manifest=manifest,
            set_owner_reference=True,
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: k8s-set-owner-reference-
    spec:
      entrypoint: k8s-set-owner-reference
      templates:
      - name: k8s-set-owner-reference
        resource:
          action: create
          manifest: "apiVersion: v1\nkind: ConfigMap\nmetadata:\n  generateName: owned-eg-\n\
            data:\n  some: value\n"
          setOwnerReference: true
    ```

