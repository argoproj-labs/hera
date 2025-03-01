# Steps With Callable Container






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Parameter, Steps, Workflow

    with Workflow(
        generate_name="steps-",
        entrypoint="hello-hello-hello",
    ) as w:
        whalesay = Container(
            name="whalesay",
            inputs=[Parameter(name="message")],
            image="docker/whalesay",
            command=["cowsay"],
            args=["{{inputs.parameters.message}}"],
        )

        with Steps(name="hello-hello-hello") as s:
            whalesay(
                name="hello1",
                arguments=[Parameter(name="message", value="hello1")],
            )

            with s.parallel():
                whalesay(
                    name="hello2a",
                    arguments=[Parameter(name="message", value="hello2a")],
                )
                whalesay(
                    name="hello2b",
                    arguments=[Parameter(name="message", value="hello2b")],
                )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: steps-
    spec:
      entrypoint: hello-hello-hello
      templates:
      - name: whalesay
        container:
          image: docker/whalesay
          args:
          - '{{inputs.parameters.message}}'
          command:
          - cowsay
        inputs:
          parameters:
          - name: message
      - name: hello-hello-hello
        steps:
        - - arguments:
              parameters:
              - name: message
                value: hello1
            name: hello1
            template: whalesay
        - - arguments:
              parameters:
              - name: message
                value: hello2a
            name: hello2a
            template: whalesay
          - arguments:
              parameters:
              - name: message
                value: hello2b
            name: hello2b
            template: whalesay
    ```

