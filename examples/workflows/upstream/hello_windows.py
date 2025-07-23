from hera.workflows import Container, Workflow

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="hello-windows-",
    entrypoint="hello-win",
) as w:
    Container(
        name="hello-win",
        node_selector={"kubernetes.io/os": "windows"},
        args=["echo", "Hello from Windows Container!"],
        command=["cmd", "/c"],
        image="mcr.microsoft.com/windows/nanoserver:1809",
    )
