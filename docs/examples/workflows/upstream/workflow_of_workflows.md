# Workflow Of Workflows

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/workflow-of-workflows.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Workflow, Resource, Parameter, Steps, Step

    with Workflow(generate_name="workflow-of-workflows-", entrypoint="main") as w:
        res_without_args = Resource(
            name="resource-without-argument",
            inputs=[Parameter(name="workflowtemplate")],
            action="create",
            manifest="""apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: workflow-of-workflows-1-
    spec:
      workflowTemplateRef:
        name: {{inputs.parameters.workflowtemplate}}
    """,
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
            manifest="""apiVersion: argoproj.io/v1alpha1
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
    """,
            success_condition="status.phase == Succeeded",
            failure_condition="status.phase in (Failed, Error)",
        )

        with Steps(name="main"):
            Step(
                name="workflow1",
                template=res_without_args,
                arguments={
                    "workflowtemplate": "workflow-template-submittable"
                }
            )
            Step(
                name="workflow2",
                template=res_with_arg,
                arguments={
                    "workflowtemplate": "workflow-template-submittable",
                    "message": "Welcome Argo",
                }
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
      - inputs:
          parameters:
          - name: workflowtemplate
        name: resource-without-argument
        resource:
          action: create
          failureCondition: status.phase in (Failed, Error)
          manifest: "apiVersion: argoproj.io/v1alpha1\nkind: Workflow\nmetadata:\n  generateName:\
            \ workflow-of-workflows-1-\nspec:\n  workflowTemplateRef:\n    name: {{inputs.parameters.workflowtemplate}}\n"
          successCondition: status.phase == Succeeded
      - inputs:
          parameters:
          - name: workflowtemplate
          - name: message
        name: resource-with-argument
        resource:
          action: create
          failureCondition: status.phase in (Failed, Error)
          manifest: "apiVersion: argoproj.io/v1alpha1\nkind: Workflow\nmetadata:\n  generateName:\
            \ workflow-of-workflows-2-\nspec:\n  arguments:\n    parameters:\n    - name:\
            \ message\n      value: {{inputs.parameters.message}}\n  workflowTemplateRef:\n\
            \    name: {{inputs.parameters.workflowtemplate}}\n"
          successCondition: status.phase == Succeeded
      - name: main
        steps:
        - - arguments:
              parameters:
              - name: workflowtemplate
                value: workflow-template-submittable
            name: workflow1
            template: resource-without-argument
        - - arguments:
              parameters:
              - name: workflowtemplate
                value: workflow-template-submittable
              - name: message
                value: Welcome Argo
            name: workflow2
            template: resource-with-argument
    ```

