from hera.workflows import Container, Step, Steps, Workflow

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="hello-hybrid-",
    entrypoint="mytemplate",
) as w:
    with Steps(
        name="mytemplate",
    ) as invocator:
        Step(
            name="step1",
            template="hello-win",
        )
        Step(
            name="step2",
            template="hello-linux",
        )
    Container(
        name="hello-win",
        node_selector={"kubernetes.io/os": "windows"},
        args=["echo", "Hello from Windows Container!"],
        command=["cmd", "/c"],
        image="mcr.microsoft.com/windows/nanoserver:1809",
    )
    Container(
        name="hello-linux",
        node_selector={"kubernetes.io/os": "linux"},
        args=["Hello from Linux Container!"],
        command=["echo"],
        image="alpine",
    )
