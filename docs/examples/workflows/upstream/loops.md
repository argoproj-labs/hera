# Loops

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/loops.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Parameter, Steps, Workflow

    with Workflow(generate_name="loops-", entrypoint="loop-example") as w:
        print_message = Container(
            name="print-message",
            inputs=Parameter(name="message"),
            image="busybox",
            command=["echo"],
            args=["{{inputs.parameters.message}}"],
        )

        with Steps(name="loop-example"):
            print_message(
                name="print-message-loop",
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
      - name: loop-example
        steps:
        - - name: print-message-loop
            template: print-message
            withItems:
            - hello world
            - goodbye world
            arguments:
              parameters:
              - name: message
                value: '{{item}}'
    ```

