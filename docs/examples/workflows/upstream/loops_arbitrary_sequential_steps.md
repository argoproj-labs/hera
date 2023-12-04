# Loops Arbitrary Sequential Steps

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/loops-arbitrary-sequential-steps.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.expr import g
    from hera.workflows import Container, Parameter, Step, Steps, Workflow

    with Workflow(
        generate_name="loop-arbitrary-sequential-steps-",
        entrypoint="loop-arbitrary-sequential-steps-example",
        arguments={  # Serialized json string used to match upstream example. You can directly use a list here instead
            "step_params": """[
      { "exit_code": 0, "message": "succeeds 1" },
      { "exit_code": 0, "message": "succeeds 2" },
      { "exit_code": 0, "message": "succeeds 3" },
      { "exit_code": 1, "message": "will fail and stop here" },
      { "exit_code": 0, "message": "will not run" },
      { "exit_code": 0, "message": "will not run" }
    ]
    """
        },
    ) as w:
        unit_step_template = Container(
            name="unit-step-template",
            image="alpine",
            command=["/bin/sh", "-c"],
            args=["echo {{inputs.parameters.message}}; exit {{inputs.parameters.exit_code}}"],
            inputs=[
                Parameter(name="exit_code"),
                Parameter(name="message"),
            ],
        )
        with Steps(
            name="loop-arbitrary-sequential-steps-example",
            inputs=[Parameter(name="step_params")],
            parallelism=1,
            fail_fast=True,
        ) as s:
            Step(
                name="unit-step",
                template=unit_step_template,
                arguments={
                    "exit_code": f"{g.item.exit_code:$}",
                    "message": f"{g.item.message:$}",
                },
                with_param=s.get_parameter("step_params"),
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: loop-arbitrary-sequential-steps-
    spec:
      arguments:
        parameters:
        - name: step_params
          value: "[\n  { \"exit_code\": 0, \"message\": \"succeeds 1\" },\n  { \"exit_code\"\
            : 0, \"message\": \"succeeds 2\" },\n  { \"exit_code\": 0, \"message\": \"\
            succeeds 3\" },\n  { \"exit_code\": 1, \"message\": \"will fail and stop here\"\
            \ },\n  { \"exit_code\": 0, \"message\": \"will not run\" },\n  { \"exit_code\"\
            : 0, \"message\": \"will not run\" }\n]\n"
      entrypoint: loop-arbitrary-sequential-steps-example
      templates:
      - container:
          args:
          - echo {{inputs.parameters.message}}; exit {{inputs.parameters.exit_code}}
          command:
          - /bin/sh
          - -c
          image: alpine
        inputs:
          parameters:
          - name: exit_code
          - name: message
        name: unit-step-template
      - failFast: true
        inputs:
          parameters:
          - name: step_params
        name: loop-arbitrary-sequential-steps-example
        parallelism: 1
        steps:
        - - arguments:
              parameters:
              - name: exit_code
                value: '{{item.exit_code}}'
              - name: message
                value: '{{item.message}}'
            name: unit-step
            template: unit-step-template
            withParam: '{{inputs.parameters.step_params}}'
    ```

