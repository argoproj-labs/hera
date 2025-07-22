# Conditionals

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/conditionals.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow
    from hera.workflows.models import Arguments, Inputs, Parameter

    with Workflow(
        arguments=Arguments(
            parameters=[
                Parameter(
                    name="should-print",
                    value="true",
                )
            ],
        ),
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="conditional-",
        entrypoint="conditional-example",
    ) as w:
        with Steps(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="should-print",
                    )
                ],
            ),
            name="conditional-example",
        ) as invocator:
            with invocator.parallel():
                Step(
                    name="print-hello-govaluate",
                    template="argosay",
                    when="{{inputs.parameters.should-print}} == true",
                )
                Step(
                    name="print-hello-expr",
                    template="argosay",
                    when="{{= inputs.parameters[\"should-print\"] == 'true'}}",
                )
                Step(
                    name="print-hello-expr-json",
                    template="argosay",
                    when="{{=jsonpath(workflow.parameters.json, '$[0].value') == 'true'}}",
                )
        Container(
            name="argosay",
            args=["cowsay hello"],
            command=["sh", "-c"],
            image="argoproj/argosay:v1",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: conditional-
    spec:
      entrypoint: conditional-example
      templates:
      - name: conditional-example
        steps:
        - - name: print-hello-govaluate
            template: argosay
            when: '{{inputs.parameters.should-print}} == true'
          - name: print-hello-expr
            template: argosay
            when: '{{= inputs.parameters["should-print"] == ''true''}}'
          - name: print-hello-expr-json
            template: argosay
            when: '{{=jsonpath(workflow.parameters.json, ''$[0].value'') == ''true''}}'
        inputs:
          parameters:
          - name: should-print
      - name: argosay
        container:
          image: argoproj/argosay:v1
          args:
          - cowsay hello
          command:
          - sh
          - -c
      arguments:
        parameters:
        - name: should-print
          value: 'true'
    ```

