# Hello Windows

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/hello-windows.yaml).




=== "Hera"

    ```python linenums="1"
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
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: hello-windows-
    spec:
      entrypoint: hello-win
      templates:
      - name: hello-win
        container:
          image: mcr.microsoft.com/windows/nanoserver:1809
          args:
          - echo
          - Hello from Windows Container!
          command:
          - cmd
          - /c
        nodeSelector:
          kubernetes.io/os: windows
    ```

