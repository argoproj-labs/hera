# Exit Handler Step Level

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/exit-handler-step-level.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Parameter, Steps, Workflow

    with Workflow(
        generate_name="exit-handler-step-level-",
        entrypoint="main",
    ) as w:
        exit_ = Container(
            name="exit",
            image="busybox",
            command=["echo"],
            args=["step cleanup"],
        )
        print_message = Container(
            name="print-message",
            inputs=[Parameter(name="message")],
            image="busybox",
            command=["echo"],
            args=["{{inputs.parameters.message}}"],
        )
        with Steps(name="main") as s:
            print_message(
                name="hello1",
                arguments=[Parameter(name="message", value="hello1")],
                on_exit=exit_,
            )
            with s.parallel():
                print_message(
                    name="hello2a",
                    arguments=[Parameter(name="message", value="hello2a")],
                    on_exit=exit_,
                )
                print_message(
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
          - echo
          image: busybox
        name: exit
      - container:
          args:
          - '{{inputs.parameters.message}}'
          command:
          - echo
          image: busybox
        inputs:
          parameters:
          - name: message
        name: print-message
      - name: main
        steps:
        - - arguments:
              parameters:
              - name: message
                value: hello1
            name: hello1
            onExit: exit
            template: print-message
        - - arguments:
              parameters:
              - name: message
                value: hello2a
            name: hello2a
            onExit: exit
            template: print-message
          - arguments:
              parameters:
              - name: message
                value: hello2b
            name: hello2b
            onExit: exit
            template: print-message
    ```

