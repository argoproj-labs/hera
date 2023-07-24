# Global Parameters

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/global-parameters.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Parameter, Workflow

    with Workflow(
        generate_name="global-parameters-",
        entrypoint="whalesay1",
        arguments=Parameter(name="message", value="hello world"),
    ) as w:
        Container(
            name="whalesay1",
            image="docker/whalesay:latest",
            command=["cowsay"],
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
      arguments:
        parameters:
        - name: message
          value: hello world
      entrypoint: whalesay1
      templates:
      - container:
          args:
          - '{{workflow.parameters.message}}'
          command:
          - cowsay
          image: docker/whalesay:latest
        name: whalesay1
    ```

