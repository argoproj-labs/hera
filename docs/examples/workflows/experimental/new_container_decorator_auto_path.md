# New Container Decorator Auto Path






=== "Hera"

    ```python linenums="1"
    from typing import Optional

    from typing_extensions import Annotated

    from hera.shared import global_config
    from hera.workflows import Container, Input, Output, Parameter, WorkflowTemplate

    global_config.experimental_features["decorator_syntax"] = True


    w = WorkflowTemplate(name="my-template")


    class MyInput(Input):
        user: str = "Hera"


    class MyOutput(Output):
        # We will let Hera figure out the output path
        container_greeting: Annotated[str, Parameter(name="container-greeting")]


    @w.set_entrypoint
    @w.container(command=["sh", "-c"])
    def advanced_hello_world(my_input: MyInput, template: Optional[Container] = None) -> MyOutput:
        output: MyOutput = MyOutput(container_greeting=f"Hello {my_input.user}")

        if template:
            # We will infer output parameter path automaically if not provided in the annotation
            template.args = [f"echo Hello {my_input.user} | tee {output.path(output.container_greeting)}"]
        return output
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: WorkflowTemplate
    metadata:
      name: my-template
    spec:
      entrypoint: advanced-hello-world
      templates:
      - container:
          args:
          - echo Hello {{inputs.parameters.user}} | tee /tmp/hera-outputs/parameters/container-greeting
          command:
          - sh
          - -c
          image: python:3.8
        inputs:
          parameters:
          - default: Hera
            name: user
        name: advanced-hello-world
        outputs:
          parameters:
          - name: container-greeting
            valueFrom:
              path: /tmp/hera-outputs/parameters/container-greeting
    ```

