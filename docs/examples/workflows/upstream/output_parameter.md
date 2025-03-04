# Output Parameter

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/output-parameter.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Container,
        Parameter,
        Steps,
        Workflow,
        models as m,
    )

    with Workflow(generate_name="output-parameter-", entrypoint="output-parameter") as w:
        hello_world_to_file = Container(
            name="hello-world-to-file",
            image="busybox",
            command=["sh", "-c"],
            args=["sleep 1; echo -n hello world > /tmp/hello_world.txt"],
            outputs=Parameter(
                name="hello-param",
                value_from=m.ValueFrom(
                    default="Foobar",
                    path="/tmp/hello_world.txt",
                ),
            ),
        )
        print_message = Container(
            name="print-message",
            image="busybox",
            command=["echo"],
            args=["{{inputs.parameters.message}}"],
            inputs=Parameter(name="message"),
        )
        with Steps(name="output-parameter"):
            g = hello_world_to_file(name="generate-parameter")
            print_message(
                name="consume-parameter",
                arguments={"message": "{{steps.generate-parameter.outputs.parameters.hello-param}}"},
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: output-parameter-
    spec:
      entrypoint: output-parameter
      templates:
      - name: hello-world-to-file
        container:
          image: busybox
          args:
          - sleep 1; echo -n hello world > /tmp/hello_world.txt
          command:
          - sh
          - -c
        outputs:
          parameters:
          - name: hello-param
            valueFrom:
              default: Foobar
              path: /tmp/hello_world.txt
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
      - name: output-parameter
        steps:
        - - name: generate-parameter
            template: hello-world-to-file
        - - name: consume-parameter
            template: print-message
            arguments:
              parameters:
              - name: message
                value: '{{steps.generate-parameter.outputs.parameters.hello-param}}'
    ```

