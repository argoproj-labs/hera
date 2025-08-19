"""This example shows how to use `TemplateRef` with `WorkflowTemplates` and `ClusterWorkflowTemplates`.

Note, running this example will attempt to create the `WorkflowTemplate` and `ClusterWorkflowTemplate` on the cluster."""

from hera.exceptions import AlreadyExists
from hera.workflows import (
    ClusterWorkflowTemplate,
    Step,
    Steps,
    Workflow,
    WorkflowsService,
    WorkflowTemplate,
    script,
)
from hera.workflows.models import TemplateRef


@script()
def hello(s: str):
    print("Hello, {s}!".format(s=s))


with WorkflowTemplate(name="hello-world-workflow-template", namespace="argo") as wt:
    hello()


with ClusterWorkflowTemplate(name="hello-world-cluster-workflow-template") as cwt:
    hello()


with Workflow(
    generate_name="use-workflow-templates-",
    entrypoint="steps",
    namespace="argo",
) as w:
    with Steps(name="steps"):
        Step(
            name="hello-template-ref",
            template_ref=TemplateRef(
                name="hello-world-workflow-template",
                template="hello",
                cluster_scope=False,
            ),
            arguments={"s": "this is using a WorkflowTemplate"},
        )
        Step(
            name="hello-cluster-template-ref",
            template_ref=TemplateRef(
                name="hello-world-cluster-workflow-template",
                template="hello",
                cluster_scope=True,
            ),
            arguments={"s": "this is using a ClusterWorkflowTemplate"},
        )

if __name__ == "__main__":
    WORKFLOWS_SERVICE = WorkflowsService(
        host="https://localhost:2746",
        verify_ssl=False,
    )
    try:
        wt.workflows_service = WORKFLOWS_SERVICE
        wt.create()
    except AlreadyExists:
        print(f"{wt.name} already exists")

    try:
        cwt.workflows_service = WORKFLOWS_SERVICE
        cwt.create()
    except AlreadyExists:
        print(f"{cwt.name} already exists")
