# Workflow Of Workflows

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/workflow-of-workflows.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Parameter, Resource, Step, Steps, Workflow
    from hera.workflows.models import WorkflowTemplateRef

    w1 = Workflow(
        generate_name="workflow-of-workflows-1-",
        workflow_template_ref=WorkflowTemplateRef(name="{{inputs.parameters.workflowtemplate}}"),
    )


    w2 = Workflow(
        generate_name="workflow-of-workflows-2-",
        arguments={"message": "{{inputs.parameters.message}}"},
        workflow_template_ref=WorkflowTemplateRef(name="{{inputs.parameters.workflowtemplate}}"),
    )

    with Workflow(generate_name="workflow-of-workflows-", entrypoint="main") as w:
        res_without_args = Resource(
            name="resource-without-argument",
            inputs=[Parameter(name="workflowtemplate")],
            action="create",
            manifest=w1,
            success_condition="status.phase == Succeeded",
            failure_condition="status.phase in (Failed, Error)",
        )

        res_with_arg = Resource(
            name="resource-with-argument",
            inputs=[
                Parameter(name="workflowtemplate"),
                Parameter(name="message"),
            ],
            action="create",
            manifest=w2,
            success_condition="status.phase == Succeeded",
            failure_condition="status.phase in (Failed, Error)",
        )

        with Steps(name="main"):
            Step(
                name="workflow1",
                template=res_without_args,
                arguments={"workflowtemplate": "workflow-template-submittable"},
            )
            Step(
                name="workflow2",
                template=res_with_arg,
                arguments={
                    "workflowtemplate": "workflow-template-submittable",
                    "message": "Welcome Argo",
                },
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: workflow-of-workflows-
    spec:
      entrypoint: main
      templates:
      - name: resource-without-argument
        inputs:
          parameters:
          - name: workflowtemplate
        resource:
          action: create
          failureCondition: status.phase in (Failed, Error)
          manifest: |
            apiVersion: argoproj.io/v1alpha1
            kind: Workflow
            metadata:
              generateName: workflow-of-workflows-1-
            spec:
              workflowTemplateRef:
                name: {{inputs.parameters.workflowtemplate}}
          successCondition: status.phase == Succeeded
      - name: resource-with-argument
        inputs:
          parameters:
          - name: workflowtemplate
          - name: message
        resource:
          action: create
          failureCondition: status.phase in (Failed, Error)
          manifest: |
            apiVersion: argoproj.io/v1alpha1
            kind: Workflow
            metadata:
              generateName: workflow-of-workflows-2-
            spec:
              arguments:
                parameters:
                - name: message
                  value: {{inputs.parameters.message}}
              workflowTemplateRef:
                name: {{inputs.parameters.workflowtemplate}}
          successCondition: status.phase == Succeeded
      - name: main
        steps:
        - - name: workflow1
            template: resource-without-argument
            arguments:
              parameters:
              - name: workflowtemplate
                value: workflow-template-submittable
        - - name: workflow2
            template: resource-with-argument
            arguments:
              parameters:
              - name: workflowtemplate
                value: workflow-template-submittable
              - name: message
                value: Welcome Argo
    ```

