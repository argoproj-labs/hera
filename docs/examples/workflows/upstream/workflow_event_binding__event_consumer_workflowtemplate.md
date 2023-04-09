# Workflow Event Binding  Event Consumer Workflowtemplate

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/workflow-event-binding/event-consumer-workflowtemplate.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Parameter, Step, Steps, WorkflowTemplate

    with WorkflowTemplate(
        name="event-consumer",
        entrypoint="main",
        arguments=Parameter(name="salutation", value="hello"),
    ) as w:
        Container(
            name="argosay",
            image="argoproj/argosay:v2",
            inputs=[
                Parameter(name="salutation"),
                Parameter(name="appellation"),
            ],
            args=["echo", "{{inputs.parameters.salutation}} {{inputs.parameters.appellation}}"],
        )
        with Steps(name="main"):
            Step(
                name="a",
                template="argosay",
                arguments=[
                    Parameter(name="salutation", value="{{workflow.parameters.salutation}}"),
                    Parameter(name="appellation", value="{{workflow.parameters.appellation}}"),
                ],
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: WorkflowTemplate
    metadata:
      name: event-consumer
    spec:
      arguments:
        parameters:
        - name: salutation
          value: hello
      entrypoint: main
      templates:
      - container:
          args:
          - echo
          - '{{inputs.parameters.salutation}} {{inputs.parameters.appellation}}'
          image: argoproj/argosay:v2
        inputs:
          parameters:
          - name: salutation
          - name: appellation
        name: argosay
      - name: main
        steps:
        - - arguments:
              parameters:
              - name: salutation
                value: '{{workflow.parameters.salutation}}'
              - name: appellation
                value: '{{workflow.parameters.appellation}}'
            name: a
            template: argosay
    ```

