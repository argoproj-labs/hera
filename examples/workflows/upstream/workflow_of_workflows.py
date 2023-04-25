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
