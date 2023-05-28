# Output Parameter

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/output-parameter.yaml).




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
        whalesay = Container(
            name="whalesay",
            image="docker/whalesay:latest",
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
            image="docker/whalesay:latest",
            command=["cowsay"],
            args=["{{inputs.parameters.message}}"],
            inputs=Parameter(name="message"),
        )
        with Steps(name="output-parameter"):
            g = whalesay(name="generate-parameter")
            print_message(name="consume-parameter", arguments={"message": "{{steps.generate-parameter.outputs.parameters.hello-param}}"})
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
      - container:
          args:
          - sleep 1; echo -n hello world > /tmp/hello_world.txt
          command:
          - sh
          - -c
          image: docker/whalesay:latest
        name: whalesay
        outputs:
          parameters:
          - name: hello-param
            valueFrom:
              default: Foobar
              path: /tmp/hello_world.txt
      - container:
          args:
          - '{{inputs.parameters.message}}'
          command:
          - cowsay
          image: docker/whalesay:latest
        inputs:
          parameters:
          - name: message
        name: print-message
      - name: output-parameter
        steps:
        - - name: generate-parameter
            template: whalesay
        - - arguments:
              parameters:
              - name: message
                value: '{{steps.generate-parameter.outputs.parameters.hello-param}}'
            name: consume-parameter
            template: print-message
    ```

