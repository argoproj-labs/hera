from hera.workflows import Container, Steps, Workflow

with Workflow(generate_name="container-on-exit-", entrypoint="step-template") as w:
    exit_container = Container(
        name="exitContainer",
        image="docker/whalesay",
        command=["cowsay"],
        args=["goodbye world"],
    )
    whalesay = Container(
        name="whalesay",
        image="docker/whalesay",
        command=["cowsay"],
        args=["hello world"],
        use_func_params_in_call=True,
    )
    with Steps(name="step-template"):
        whalesay().with_(name="stepA", on_exit=exit_container)
        whalesay().with_(name="stepB", on_exit=exit_container)
