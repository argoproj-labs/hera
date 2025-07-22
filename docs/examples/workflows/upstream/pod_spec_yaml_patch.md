# Pod Spec Yaml Patch

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/pod-spec-yaml-patch.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Workflow
    from hera.workflows.models import Arguments, Parameter

    with Workflow(
        arguments=Arguments(
            parameters=[
                Parameter(
                    name="mem-limit",
                    value="100Mi",
                )
            ],
        ),
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="pod-spec-patch-",
        entrypoint="hello-world",
        pod_spec_patch='containers:\n  - name: main\n    resources:\n      limits:\n        memory: "{{workflow.parameters.mem-limit}}"\n',
    ) as w:
        Container(
            name="hello-world",
            args=["hello world"],
            command=["echo"],
            image="busybox",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: pod-spec-patch-
    spec:
      entrypoint: hello-world
      podSpecPatch: |
        containers:
          - name: main
            resources:
              limits:
                memory: "{{workflow.parameters.mem-limit}}"
      templates:
      - name: hello-world
        container:
          image: busybox
          args:
          - hello world
          command:
          - echo
      arguments:
        parameters:
        - name: mem-limit
          value: 100Mi
    ```

