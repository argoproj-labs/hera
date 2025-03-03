# Global Parameters

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/global-parameters.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Parameter, Workflow

    with Workflow(
        generate_name="global-parameters-",
        entrypoint="print-message",
        arguments=Parameter(name="message", value="hello world"),
    ) as w:
        Container(
            name="print-message",
            image="busybox",
            command=["echo"],
            args=["{{workflow.parameters.message}}"],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: global-parameters-
    spec:
      entrypoint: print-message
      templates:
      - name: print-message
        container:
          image: busybox
          args:
          - '{{workflow.parameters.message}}'
          command:
          - echo
      arguments:
        parameters:
        - name: message
          value: hello world
    ```

