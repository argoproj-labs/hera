from hera.workflows import Container, Parameter, Steps, Workflow

with Workflow(generate_name="loops-", entrypoint="loop-example") as w:
    print_message = Container(
        name="print-message",
        inputs=Parameter(name="message"),
        image="busybox",
        command=["echo"],
        args=["{{inputs.parameters.message}}"],
    )

    with Steps(name="loop-example"):
        print_message(
            name="print-message-loop",
            arguments={"message": "{{item}}"},
            with_items=["hello world", "goodbye world"],
        )
