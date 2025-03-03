# Exit Handler Step Level

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/exit-handler-step-level.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Parameter, Steps, Workflow
    from hera.workflows.models import LifecycleHook

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
                hooks={"exit": LifecycleHook(template=exit_.name)},
            )
            with s.parallel():
                print_message(
                    name="hello2a",
                    arguments=[Parameter(name="message", value="hello2a")],
                    hooks={"exit": LifecycleHook(template=exit_.name)},
                )
                print_message(
                    name="hello2b",
                    arguments=[Parameter(name="message", value="hello2b")],
                    hooks={"exit": LifecycleHook(template=exit_.name)},
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
      - name: exit
        container:
          image: busybox
          args:
          - step cleanup
          command:
          - echo
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
      - name: main
        steps:
        - - arguments:
              parameters:
              - name: message
                value: hello1
            hooks:
              exit:
                template: exit
            name: hello1
            template: print-message
        - - arguments:
              parameters:
              - name: message
                value: hello2a
            hooks:
              exit:
                template: exit
            name: hello2a
            template: print-message
          - arguments:
              parameters:
              - name: message
                value: hello2b
            hooks:
              exit:
                template: exit
            name: hello2b
            template: print-message
    ```

