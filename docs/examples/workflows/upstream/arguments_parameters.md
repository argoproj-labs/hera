# Arguments Parameters

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/arguments-parameters.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Parameter, Workflow

    with Workflow(
        generate_name="arguments-parameters-",
        entrypoint="print-message",
        arguments=Parameter(name="message", value="hello world"),
    ) as w:
        Container(
            name="print-message",
            image="busybox",
            command=["echo"],
            args=["{{inputs.parameters.message}}"],
            inputs=Parameter(name="message"),
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: arguments-parameters-
    spec:
      arguments:
        parameters:
        - name: message
          value: hello world
      entrypoint: print-message
      templates:
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
    ```

