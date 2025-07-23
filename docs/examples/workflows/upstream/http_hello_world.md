# Http Hello World

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/http-hello-world.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import HTTP, Step, Steps, Workflow
    from hera.workflows.models import Arguments, ContinueOn, Inputs, Parameter

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        annotations={
            "workflows.argoproj.io/description": "Http template will demostrate http template functionality\n",
            "workflows.argoproj.io/version": ">= 3.2.0",
        },
        generate_name="http-template-",
        labels={"workflows.argoproj.io/test": "true"},
        entrypoint="main",
    ) as w:
        with Steps(
            name="main",
        ) as invocator:
            with invocator.parallel():
                Step(
                    arguments=Arguments(
                        parameters=[
                            Parameter(
                                name="url",
                                value="https://raw.githubusercontent.com/argoproj/argo-workflows/4e450e250168e6b4d51a126b784e90b11a0162bc/pkg/apis/workflow/v1alpha1/generated.swagger.json",
                            )
                        ],
                    ),
                    name="good",
                    template="http",
                )
                Step(
                    arguments=Arguments(
                        parameters=[
                            Parameter(
                                name="url",
                                value="https://raw.githubusercontent.com/argoproj/argo-workflows/thisisnotahash/pkg/apis/workflow/v1alpha1/generated.swagger.json",
                            )
                        ],
                    ),
                    name="bad",
                    continue_on=ContinueOn(
                        failed=True,
                    ),
                    template="http",
                )
        HTTP(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="url",
                    )
                ],
            ),
            name="http",
            url="{{inputs.parameters.url}}",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: http-template-
      annotations:
        workflows.argoproj.io/description: |
          Http template will demostrate http template functionality
        workflows.argoproj.io/version: '>= 3.2.0'
      labels:
        workflows.argoproj.io/test: 'true'
    spec:
      entrypoint: main
      templates:
      - name: main
        steps:
        - - name: good
            template: http
            arguments:
              parameters:
              - name: url
                value: https://raw.githubusercontent.com/argoproj/argo-workflows/4e450e250168e6b4d51a126b784e90b11a0162bc/pkg/apis/workflow/v1alpha1/generated.swagger.json
          - name: bad
            template: http
            arguments:
              parameters:
              - name: url
                value: https://raw.githubusercontent.com/argoproj/argo-workflows/thisisnotahash/pkg/apis/workflow/v1alpha1/generated.swagger.json
            continueOn:
              failed: true
      - name: http
        http:
          url: '{{inputs.parameters.url}}'
        inputs:
          parameters:
          - name: url
    ```

