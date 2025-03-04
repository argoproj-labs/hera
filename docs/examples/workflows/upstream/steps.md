# Steps

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/steps.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Parameter, Step, Steps, Workflow

    with Workflow(
        generate_name="steps-",
        entrypoint="hello-hello-hello",
    ) as w:
        print_message = Container(
            name="print-message",
            inputs=[Parameter(name="message")],
            image="busybox",
            command=["echo"],
            args=["{{inputs.parameters.message}}"],
        )

        with Steps(name="hello-hello-hello") as s:
            Step(
                name="hello1",
                template=print_message,
                arguments=[Parameter(name="message", value="hello1")],
            )

            with s.parallel():
                Step(
                    name="hello2a",
                    template=print_message,
                    arguments=[Parameter(name="message", value="hello2a")],
                )
                Step(
                    name="hello2b",
                    template=print_message,
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
      - name: print-message
        container:
          image: busybox
          args:
          - '{{inputs.parameters.message}}'
          command:
          - echo
        inputs:
          parameters:
          - name: message
      - name: hello-hello-hello
        steps:
        - - name: hello1
            template: print-message
            arguments:
              parameters:
              - name: message
                value: hello1
        - - name: hello2a
            template: print-message
            arguments:
              parameters:
              - name: message
                value: hello2a
          - name: hello2b
            template: print-message
            arguments:
              parameters:
              - name: message
                value: hello2b
    ```

