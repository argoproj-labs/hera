# New Container Decorator






=== "Hera"

    ```python linenums="1"
    from typing_extensions import Annotated

    from hera.shared import global_config
    from hera.workflows import Input, Output, Parameter, WorkflowTemplate

    global_config.experimental_features["decorator_syntax"] = True


    # We start by defining our Workflow Template
    w = WorkflowTemplate(name="my-template")


    # This defines the template's inputs
    class MyInput(Input):
        user: str = "Hera"


    class MyOutput(Output):
        container_greeting: Annotated[
            str,
            Parameter(
                name="container-greeting",
                value_from={"path": "/tmp/hello_world.txt"},
            ),
        ]


    @w.set_entrypoint
    @w.container(
        image="busybox",
        command=["sh", "-c"],
        args=["echo Hello {{inputs.parameters.user}} | tee /tmp/hello_world.txt"],
    )
    def basic_hello_world(my_input: MyInput) -> MyOutput: ...
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: WorkflowTemplate
    metadata:
      name: my-template
    spec:
      entrypoint: basic-hello-world
      templates:
      - container:
          args:
          - echo Hello {{inputs.parameters.user}} | tee /tmp/hello_world.txt
          command:
          - sh
          - -c
          image: busybox
        inputs:
          parameters:
          - default: Hera
            name: user
        name: basic-hello-world
        outputs:
          parameters:
          - name: container-greeting
            valueFrom:
              path: /tmp/hello_world.txt
    ```

