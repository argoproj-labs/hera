from hera.workflows import Parameter, Resource, Step, Steps, Workflow
from hera.workflows.models import WorkflowTemplateRef

w1 = Workflow(
    generate_name="workflow-of-workflows-1-",
    workflow_template_ref=WorkflowTemplateRef(name="{{inputs.parameters.workflowtemplate}}"),
)

w1_yaml = w1.to_yaml().replace("'{{", "{{").replace("}}'", "}}")  # hack to appease raw yaml string comparison

w2 = Workflow(
    generate_name="workflow-of-workflows-2-",
    arguments={"message": "{{inputs.parameters.message}}"},
    workflow_template_ref=WorkflowTemplateRef(name="{{inputs.parameters.workflowtemplate}}"),
)
w2_yaml = w2.to_yaml().replace("'{{", "{{").replace("}}'", "}}")  # hack to appease raw yaml string comparison

with Workflow(generate_name="workflow-of-workflows-", entrypoint="main") as w:
    res_without_args = Resource(
        name="resource-without-argument",
        inputs=[Parameter(name="workflowtemplate")],
        action="create",
        manifest=w1_yaml,
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
        manifest=w2_yaml,
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
