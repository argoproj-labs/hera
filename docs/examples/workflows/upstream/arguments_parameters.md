# Arguments Parameters

> Note: This example is a replication of an Argo Workflow example in Hera. 




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Parameter, Workflow

    with Workflow(
        generate_name="arguments-parameters-",
        entrypoint="whalesay",
        arguments=Parameter(name="message", value="hello world"),
    ) as w:
        Container(
            name="whalesay",
            image="docker/whalesay:latest",
            command=["cowsay"],
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
      entrypoint: whalesay
      templates:
      - container:
          args:
          - '{{inputs.parameters.message}}'
          command:
          - cowsay
          image: docker/whalesay:latest
        inputs:
          parameters:
          - name: message
        name: whalesay
    ```

