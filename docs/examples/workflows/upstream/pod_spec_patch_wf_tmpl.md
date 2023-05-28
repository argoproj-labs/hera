# Pod Spec Patch Wf Tmpl

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/pod-spec-patch-wf-tmpl.yaml).




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
        entrypoint="whalesay",
        pod_spec_patch=pod_spec_patch,
        arguments=[Parameter(name="cpu-limit", value="100m"), Parameter(name="mem-limit", value="100Mi")],
    ) as w:
        whalesay = Container(
            name="whalesay",
            image="docker/whalesay:latest",
            command=["cowsay"],
            args=["hello world"],
            pod_spec_patch='{"containers":[{"name":"main", "resources":{"limits":{"cpu": "{{workflow.parameters.cpu-limit}}" }}}]}',
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
      entrypoint: whalesay
      podSpecPatch: "containers:\n  - name: main\n    resources:\n      limits:\n    \
        \    memory: \"{{workflow.parameters.mem-limit}}\"\n"
      templates:
      - container:
          args:
          - hello world
          command:
          - cowsay
          image: docker/whalesay:latest
        name: whalesay
        podSpecPatch: '{"containers":[{"name":"main", "resources":{"limits":{"cpu": "{{workflow.parameters.cpu-limit}}"
          }}}]}'
    ```

