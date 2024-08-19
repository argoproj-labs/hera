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
