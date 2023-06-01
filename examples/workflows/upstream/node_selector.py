from hera.workflows import Container, Parameter, Workflow

with Workflow(
    generate_name="node-selector-",
    entrypoint="print-arch",
    arguments=Parameter(name="arch", value="amd64"),
) as w:
    print_arch = Container(
        name="print-arch",
        inputs=[Parameter(name="arch")],
        image="alpine:latest",
        command=["sh", "-c"],
        args=["uname -a"],
        node_selector={"beta.kubernetes.io/arch": "{{inputs.parameters.arch}}"},
    )
