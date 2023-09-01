from hera.workflows import Container, Parameter, Steps, Workflow

with Workflow(generate_name="loops-", entrypoint="loop-example") as w:
    whalesay = Container(
        name="whalesay",
        inputs=Parameter(name="message"),
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=["{{inputs.parameters.message}}"],
        directly_callable=True,
    )

    with Steps(name="loop-example"):
        whalesay(
            "{{item}}",
        ).with_(
            name="print-message",
            with_items=["hello world", "goodbye world"],
        )
