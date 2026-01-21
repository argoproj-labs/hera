# Suspend Input Duration






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Parameter, Step, Steps, Suspend, Workflow

    with Workflow(
        generate_name="suspend-input-duration-",
        entrypoint="suspend",
    ) as w:
        intermediate_params = Suspend(
            name="suspend-with-intermediate-param",
            intermediate_parameters=[Parameter(name="duration")],
        )

        configurable_suspend_template = Suspend(
            name="input-duration-suspend",
            inputs=[Parameter(name="duration", default="10")],
            duration="{{inputs.parameters.duration}}",
        )

        with Steps(name="suspend"):
            get_value_step = intermediate_params(name="get-value-step")

            Step(
                name="custom-delay-step",
                template=configurable_suspend_template,
                arguments={"duration": get_value_step.get_parameter("duration")},
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: suspend-input-duration-
    spec:
      entrypoint: suspend
      templates:
      - name: suspend-with-intermediate-param
        inputs:
          parameters:
          - name: duration
        outputs:
          parameters:
          - name: duration
            valueFrom:
              supplied: {}
        suspend: {}
      - name: input-duration-suspend
        inputs:
          parameters:
          - name: duration
            default: '10'
        suspend:
          duration: '{{inputs.parameters.duration}}'
      - name: suspend
        steps:
        - - name: get-value-step
            template: suspend-with-intermediate-param
        - - name: custom-delay-step
            template: input-duration-suspend
            arguments:
              parameters:
              - name: duration
                value: '{{steps.get-value-step.outputs.parameters.duration}}'
    ```

