# Suspend Input Duration






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Step, Steps, Suspend, Workflow
    from hera.workflows.models import Inputs, Parameter, SuspendTemplate, Template

    with Workflow(
        generate_name="suspend-input-duration-",
        entrypoint="suspend",
    ) as w:
        intermediate_params = Suspend(
            name="suspend-with-intermediate-param",
            intermediate_parameters=[Parameter(name="duration")],
        )

        configurable_suspend_template = Template(
            name="input-duration-suspend",
            suspend=SuspendTemplate(duration="{{inputs.parameters.duration}}"),
            inputs=Inputs(parameters=[Parameter(name="duration", default="10")]),
        )

        with Steps(name="suspend"):
            intermediate_params(name="get-value-step")

            Step(
                name="custom-delay-step",
                template=configurable_suspend_template,
                arguments={"duration": "{{steps.get-value-step.outputs.parameters.duration}}"},
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
      - inputs:
          parameters:
          - default: 'null'
            name: duration
            value: 'null'
        name: suspend-with-intermediate-param
        outputs:
          parameters:
          - name: duration
            valueFrom:
              supplied: {}
        suspend: {}
      - name: suspend
        steps:
        - - name: get-value-step
            template: suspend-with-intermediate-param
        - - arguments:
              parameters:
              - name: duration
                value: '{{steps.get-value-step.outputs.parameters.duration}}'
            name: custom-delay-step
            template: input-duration-suspend
      - inputs:
          parameters:
          - default: '10'
            name: duration
        name: input-duration-suspend
        suspend:
          duration: '{{inputs.parameters.duration}}'
    ```

