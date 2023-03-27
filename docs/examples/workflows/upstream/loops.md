# Loops

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/loops.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Parameter, Steps, Workflow

    with Workflow(generate_name="loops-", entrypoint="loop-example") as w:
        whalesay = Container(
            name="whalesay",
            inputs=Parameter(name="message"),
            image="docker/whalesay:latest",
            command=["cowsay"],
            args=["{{inputs.parameters.message}}"],
        )

        with Steps(name="loop-example"):
            whalesay(
                name="print-message",
                arguments={"message": "{{item}}"},
                with_items=["hello world", "goodbye world"],
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: loops-
    spec:
      entrypoint: loop-example
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
      - name: loop-example
        steps:
        - - arguments:
              parameters:
              - name: message
                value: '{{item}}'
            name: print-message
            template: whalesay
            withItems:
            - hello world
            - goodbye world
    ```

