# Pod Spec Patch Wf Tmpl

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/pod-spec-patch-wf-tmpl.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Parameter, Workflow

    pod_spec_patch = """containers:
      - name: main
        resources:
          limits:
            memory: "{{workflow.parameters.mem-limit}}\"
    """
    with Workflow(
        generate_name="pod-spec-patch-",
        entrypoint="hello-world",
        pod_spec_patch=pod_spec_patch,
        arguments=[Parameter(name="cpu-limit", value="100m"), Parameter(name="mem-limit", value="100Mi")],
    ) as w:
        print_message = Container(
            name="hello-world",
            image="busybox",
            command=["echo"],
            args=["hello world"],
            pod_spec_patch='{"containers":[{"name":"main", "resources":{"limits":{"cpu": '
            '"{{workflow.parameters.cpu-limit}}" }}}]}',
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: pod-spec-patch-
    spec:
      arguments:
        parameters:
        - name: cpu-limit
          value: 100m
        - name: mem-limit
          value: 100Mi
      entrypoint: hello-world
      podSpecPatch: |
        containers:
          - name: main
            resources:
              limits:
                memory: "{{workflow.parameters.mem-limit}}"
      templates:
      - container:
          args:
          - hello world
          command:
          - echo
          image: busybox
        name: hello-world
        podSpecPatch: '{"containers":[{"name":"main", "resources":{"limits":{"cpu": "{{workflow.parameters.cpu-limit}}"
          }}}]}'
    ```

