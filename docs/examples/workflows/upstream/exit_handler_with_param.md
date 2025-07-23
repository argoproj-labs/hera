# Exit Handler With Param

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/exit-handler-with-param.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Script, Step, Steps, Workflow
    from hera.workflows.models import Arguments, Inputs, LifecycleHook, Outputs, Parameter, ValueFrom

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        annotations={
            "workflows.argoproj.io/description": "onExitTemplate enables workflow to pass the arguments (parameters/Artifacts) to exit handler template.\n",
            "workflows.argoproj.io/version": ">= 3.1.0",
        },
        generate_name="exit-handler-with-param-",
        labels={"workflows.argoproj.io/test": "true"},
        entrypoint="main",
    ) as w:
        with Steps(
            name="main",
        ) as invocator:
            Step(
                name="step-1",
                hooks={
                    "exit": LifecycleHook(
                        arguments=Arguments(
                            parameters=[
                                Parameter(
                                    name="message",
                                    value="{{steps.step-1.outputs.parameters.result}}",
                                )
                            ],
                        ),
                        template="exit",
                    )
                },
                template="output",
            )
        Container(
            name="output",
            outputs=Outputs(
                parameters=[
                    Parameter(
                        name="result",
                        value_from=ValueFrom(
                            default="Foobar",
                            path="/tmp/hello_world.txt",
                        ),
                    )
                ],
            ),
            args=["echo -n hello world > /tmp/hello_world.txt"],
            command=["sh", "-c"],
            image="python:alpine3.6",
        )
        Script(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="message",
                    )
                ],
            ),
            name="exit",
            command=["python"],
            image="python:alpine3.6",
            source='print("{{inputs.parameters.message}}")',
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: exit-handler-with-param-
      annotations:
        workflows.argoproj.io/description: |
          onExitTemplate enables workflow to pass the arguments (parameters/Artifacts) to exit handler template.
        workflows.argoproj.io/version: '>= 3.1.0'
      labels:
        workflows.argoproj.io/test: 'true'
    spec:
      entrypoint: main
      templates:
      - name: main
        steps:
        - - name: step-1
            template: output
            hooks:
              exit:
                template: exit
                arguments:
                  parameters:
                  - name: message
                    value: '{{steps.step-1.outputs.parameters.result}}'
      - name: output
        container:
          image: python:alpine3.6
          args:
          - echo -n hello world > /tmp/hello_world.txt
          command:
          - sh
          - -c
        outputs:
          parameters:
          - name: result
            valueFrom:
              default: Foobar
              path: /tmp/hello_world.txt
      - name: exit
        inputs:
          parameters:
          - name: message
        script:
          image: python:alpine3.6
          source: print("{{inputs.parameters.message}}")
          command:
          - python
    ```

