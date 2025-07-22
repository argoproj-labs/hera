from hera.workflows import Script, WorkflowTemplate
from hera.workflows.models import Arguments, Inputs, Parameter

with WorkflowTemplate(
    arguments=Arguments(
        parameters=[
            Parameter(
                name="date",
                value="yesterday",
            )
        ],
    ),
    api_version="argoproj.io/v1alpha1",
    kind="WorkflowTemplate",
    name="job",
    entrypoint="main",
) as w:
    Script(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="date",
                )
            ],
        ),
        name="main",
        command=["sh"],
        image="busybox",
        source='date="{{inputs.parameters.date}}"\nif [ $date = yesterday ]; then\n  date=$(date -d yesterday +%Y-%m-%d)\nfi\necho "run for $date"\n',
    )
from hera.workflows import CronWorkflow
from hera.workflows.models import WorkflowTemplateRef

with CronWorkflow(
    api_version="argoproj.io/v1alpha1",
    kind="CronWorkflow",
    name="daily-job",
    workflow_template_ref=WorkflowTemplateRef(
        name="job",
    ),
    schedule="0 2 * * *",
) as w:
    pass

from hera.workflows import Resource, Step, Steps, Workflow
from hera.workflows.models import Arguments, Inputs, IntOrString, Parameter, Sequence

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    name="backfill-v1",
    entrypoint="main",
    service_account_name="argo-server",
) as w:
    with Steps(
        name="main",
    ) as invocator:
        Step(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="date",
                        value="{{item}}",
                    )
                ],
            ),
            name="day",
            template="create-job",
            with_sequence=Sequence(
                end=IntOrString(
                    __root__="21",
                ),
                format="2020-05-%02X",
                start=IntOrString(
                    __root__="19",
                ),
            ),
        )
    Resource(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="date",
                )
            ],
        ),
        name="create-job",
        action="apply",
        manifest='apiVersion: argoproj.io/v1alpha1\nkind: Workflow\nmetadata:\n  # using a name based on the date prevents re-creating resources,\n  # making this more robust\n  name: job-{{inputs.parameters.date}}\nspec:\n  entrypoint: main\n  templates:\n    - name: main\n      steps:\n        - - name: start-job\n            arguments:\n              parameters:\n                - name: date\n                  value: "{{inputs.parameters.date}}"\n            templateRef:\n              name: job\n              template: main\n',
    )
from hera.workflows import Step, Steps, Workflow
from hera.workflows.models import Arguments, IntOrString, Parameter, Sequence, TemplateRef

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    name="backfill-v2",
    entrypoint="main",
    parallelism=1,
) as w:
    with Steps(
        name="main",
    ) as invocator:
        Step(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="date",
                        value="{{item}}",
                    )
                ],
            ),
            name="create-job",
            template_ref=TemplateRef(
                name="job",
                template="main",
            ),
            with_sequence=Sequence(
                end=IntOrString(
                    __root__="21",
                ),
                format="2020-05-%02X",
                start=IntOrString(
                    __root__="19",
                ),
            ),
        )
