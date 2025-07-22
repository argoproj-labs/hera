# Hello Hybrid

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/hello-hybrid.yaml).




=== "Hera"

    ```python linenums="1"
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
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: hello-hybrid-
    spec:
      entrypoint: mytemplate
      templates:
      - name: mytemplate
        steps:
        - - name: step1
            template: hello-win
        - - name: step2
            template: hello-linux
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
      - name: hello-linux
        container:
          image: alpine
          args:
          - Hello from Linux Container!
          command:
          - echo
        nodeSelector:
          kubernetes.io/os: linux
    ```

