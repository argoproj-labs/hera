from hera.workflows import DAG, Script, Task, Workflow
from hera.workflows.models import Arguments, Inputs, Outputs, Parameter, ValueFrom

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="pod-spec-from-previous-step-",
    entrypoint="workflow",
) as w:
    with DAG(
        name="workflow",
    ) as invocator:
        Task(
            name="parse-resources",
            template="parse-resources-tmpl",
        )
        Task(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="resources",
                        value="{{tasks.parse-resources.outputs.parameters.resources}}",
                    )
                ],
            ),
            name="setup-resources",
            template="setup-resources-tmpl",
            depends="parse-resources",
        )
    Script(
        name="parse-resources-tmpl",
        outputs=Outputs(
            parameters=[
                Parameter(
                    name="resources",
                    value_from=ValueFrom(
                        path="/tmp/resources.json",
                    ),
                )
            ],
        ),
        command=["sh"],
        image="alpine:latest",
        source='echo \'{"memory": "10Gi", "cpu": "2000m"}\' > /tmp/resources.json && cat /tmp/resources.json\n',
    )
    Script(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="resources",
                )
            ],
        ),
        name="setup-resources-tmpl",
        pod_spec_patch='{"containers":[{"name":"main", "resources":{"limits": {{inputs.parameters.resources}}, "requests": {{inputs.parameters.resources}} }}]}',
        command=["sh"],
        image="alpine:latest",
        source="echo {{inputs.parameters.resources}}\n",
    )
