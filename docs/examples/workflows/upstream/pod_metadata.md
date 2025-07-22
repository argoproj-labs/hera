# Pod Metadata

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/pod-metadata.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow
    from hera.workflows.models import Arguments, Inputs, Parameter

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="steps-",
        entrypoint="hello-hello-hello",
    ) as w:
        with Steps(
            name="hello-hello-hello",
        ) as invocator:
            Step(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="message",
                            value="hello1",
                        )
                    ],
                ),
                name="hello1",
                template="print-message",
            )
        Container(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="message",
                    )
                ],
            ),
            labels={"app": "print-message", "tier": "demo"},
            annotations={"iam.amazonaws.com/role": "role-arn"},
            name="print-message",
            args=["{{inputs.parameters.message}}"],
            command=["echo"],
            image="busybox",
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
      - name: hello-hello-hello
        steps:
        - - name: hello1
            template: print-message
            arguments:
              parameters:
              - name: message
                value: hello1
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
        metadata:
          annotations:
            iam.amazonaws.com/role: role-arn
          labels:
            app: print-message
            tier: demo
    ```

