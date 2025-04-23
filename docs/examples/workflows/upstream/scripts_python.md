# Scripts Python

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/scripts-python.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Parameter, Script, Step, Steps, Workflow

    with Workflow(
        generate_name="scripts-python-",
        entrypoint="python-script-example",
    ) as w:
        gen_random_int = Script(
            name="gen-random-int",
            image="python:alpine3.6",
            command=["python"],
            source="""
    import random
    i = random.randint(1, 100)
    print(i)""",
        )

        print_message = Container(
            name="print-message",
            image="alpine:latest",
            command=["sh", "-c"],
            args=["echo result was: {{inputs.parameters.message}}"],
            inputs=[Parameter(name="message")],
        )

        with Steps(name="python-script-example") as s:
            Step(
                name="generate",
                template="gen-random-int",
            )
            Step(
                name="print",
                template="print-message",
                arguments={"message": "{{steps.generate.outputs.result}}"},
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: scripts-python-
    spec:
      entrypoint: python-script-example
      templates:
      - name: gen-random-int
        script:
          image: python:alpine3.6
          source: |2-

            import random
            i = random.randint(1, 100)
            print(i)
          command:
          - python
      - name: print-message
        container:
          image: alpine:latest
          args:
          - 'echo result was: {{inputs.parameters.message}}'
          command:
          - sh
          - -c
        inputs:
          parameters:
          - name: message
      - name: python-script-example
        steps:
        - - name: generate
            template: gen-random-int
        - - name: print
            template: print-message
            arguments:
              parameters:
              - name: message
                value: '{{steps.generate.outputs.result}}'
    ```

