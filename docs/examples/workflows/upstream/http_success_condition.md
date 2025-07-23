# Http Success Condition

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/http-success-condition.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import HTTP, Step, Steps, Workflow
    from hera.workflows.models import Arguments, Inputs, Parameter

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        annotations={
            "workflows.argoproj.io/description": "Exemplifies usage of successCondition in HTTP template (available since v3.3)\n"
        },
        generate_name="http-template-condition-",
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
                                value="http://httpstat.us/201",
                            )
                        ],
                    ),
                    name="http-status-is-201-succeeds",
                    template="http-status-is-201",
                )
                Step(
                    arguments=Arguments(
                        parameters=[
                            Parameter(
                                name="url",
                                value="https://google.com",
                            )
                        ],
                    ),
                    name="http-body-contains-google-succeeds",
                    template="http-body-contains-google",
                )
        HTTP(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="url",
                    )
                ],
            ),
            name="http-status-is-201",
            success_condition="response.statusCode == 201",
            url="{{inputs.parameters.url}}",
        )
        HTTP(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="url",
                    )
                ],
            ),
            name="http-body-contains-google",
            success_condition='response.body contains "google"',
            url="{{inputs.parameters.url}}",
        )
        HTTP(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="url",
                    )
                ],
            ),
            name="http-headers-contains-cloudflare",
            success_condition='response.headers["Server"][0] == "cloudflare"',
            url="{{inputs.parameters.url}}",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: http-template-condition-
      annotations:
        workflows.argoproj.io/description: |
          Exemplifies usage of successCondition in HTTP template (available since v3.3)
    spec:
      entrypoint: main
      templates:
      - name: main
        steps:
        - - name: http-status-is-201-succeeds
            template: http-status-is-201
            arguments:
              parameters:
              - name: url
                value: http://httpstat.us/201
          - name: http-body-contains-google-succeeds
            template: http-body-contains-google
            arguments:
              parameters:
              - name: url
                value: https://google.com
      - name: http-status-is-201
        http:
          successCondition: response.statusCode == 201
          url: '{{inputs.parameters.url}}'
        inputs:
          parameters:
          - name: url
      - name: http-body-contains-google
        http:
          successCondition: response.body contains "google"
          url: '{{inputs.parameters.url}}'
        inputs:
          parameters:
          - name: url
      - name: http-headers-contains-cloudflare
        http:
          successCondition: response.headers["Server"][0] == "cloudflare"
          url: '{{inputs.parameters.url}}'
        inputs:
          parameters:
          - name: url
    ```

