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
        pod_spec_patch='{"containers":[{"name":"main", "resources":{"limits":{"cpu": '
        '"{{workflow.parameters.cpu-limit}}" }}}]}',
    )
