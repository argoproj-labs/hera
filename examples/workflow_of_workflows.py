from hera import ResourceTemplate, Task, Variable, Workflow, WorkflowService


def get_resource_template_no_args():
    manifest = """
          apiVersion: argoproj.io/v1alpha1
          kind: Workflow
          metadata:
            generateName: workflow-of-workflows-1-
          spec:
            workflowTemplateRef:
              name: {{inputs.parameters.workflowtemplate}}
        """
    resource_template = ResourceTemplate(
        action="create",
        manifest=manifest,
        success_condition="status.phase == Succeeded",
        failure_condition="status.phase in (Failed, Error)",
    )
    return resource_template


def get_resource_template_with_args():
    manifest = """
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
        """
    resource_template = ResourceTemplate(
        action="create",
        manifest=manifest,
        success_condition="status.phase == Succeeded",
        failure_condition="status.phase in (Failed, Error)",
    )
    return resource_template


# TODO: replace the domain, token and workflow template name with your own
ws = WorkflowService(host="", token="")
w = Workflow(f"workflow-of-workflows", ws)
t1 = Task(
    "t1",
    variables=[Variable(name="workflowtemplate", value="put-your-own-workflow-template-name-here")],
    resource_template=get_resource_template_no_args(),
)
t2 = Task(
    "t2",
    variables=[
        Variable(name="workflowtemplate", value="put-your-own-workflow-template-name-here"),
        Variable(name="message", value="Welcome Hera"),
    ],
    resource_template=get_resource_template_with_args(),
)
t1 >> t2
w.add_tasks(t1, t2)
w.create(namespace="argo")
