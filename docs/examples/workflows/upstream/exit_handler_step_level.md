# Exit Handler Step Level

> Note: This example is a replication of an Argo Workflow example in Hera. 




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Parameter, Steps, Workflow

    with Workflow(
        generate_name="exit-handler-step-level-",
        entrypoint="main",
    ) as w:
        exit_ = Container(
            name="exit",
            image="docker/whalesay",
            command=["cowsay"],
            args=["step cleanup"],
        )
        whalesay = Container(
            name="whalesay",
            inputs=[Parameter(name="message")],
            image="docker/whalesay",
            command=["cowsay"],
            args=["{{inputs.parameters.message}}"],
        )
        with Steps(name="main") as s:
            whalesay(
                name="hello1",
                arguments=[Parameter(name="message", value="hello1")],
                on_exit=exit_,
            )
            with s.parallel():
                whalesay(
                    name="hello2a",
                    arguments=[Parameter(name="message", value="hello2a")],
                    on_exit=exit_,
                )
                whalesay(
                    name="hello2b",
                    arguments=[Parameter(name="message", value="hello2b")],
                    on_exit=exit_,
                )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: exit-handler-step-level-
    spec:
      entrypoint: main
      templates:
      - container:
          args:
          - step cleanup
          command:
          - cowsay
          image: docker/whalesay
        name: exit
      - container:
          args:
          - '{{inputs.parameters.message}}'
          command:
          - cowsay
          image: docker/whalesay
        inputs:
          parameters:
          - name: message
        name: whalesay
      - name: main
        steps:
        - - arguments:
              parameters:
              - name: message
                value: hello1
            name: hello1
            onExit: exit
            template: whalesay
        - - arguments:
              parameters:
              - name: message
                value: hello2a
            name: hello2a
            onExit: exit
            template: whalesay
          - arguments:
              parameters:
              - name: message
                value: hello2b
            name: hello2b
            onExit: exit
            template: whalesay
    ```

