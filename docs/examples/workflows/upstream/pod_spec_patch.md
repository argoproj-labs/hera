# Pod Spec Patch

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/pod-spec-patch.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Workflow
    from hera.workflows.models import Arguments, Parameter

    with Workflow(
        arguments=Arguments(
            parameters=[
                Parameter(
                    name="cpu-limit",
                    value="100m",
                )
            ],
        ),
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="pod-spec-patch-",
        entrypoint="hello-world",
    ) as w:
        Container(
            name="hello-world",
            pod_spec_patch='{"containers":[{"name":"main", "resources":{"limits":{"cpu": "{{workflow.parameters.cpu-limit}}" }}}]}',
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
      templates:
      - name: hello-world
        podSpecPatch: '{"containers":[{"name":"main", "resources":{"limits":{"cpu": "{{workflow.parameters.cpu-limit}}"
          }}}]}'
        container:
          image: busybox
          args:
          - hello world
          command:
          - echo
      arguments:
        parameters:
        - name: cpu-limit
          value: 100m
    ```

