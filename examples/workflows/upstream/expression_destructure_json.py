from hera.workflows import Script, Workflow
from hera.workflows.models import Arguments, EnvVar, Inputs, Parameter

with Workflow(
    arguments=Arguments(
        parameters=[
            Parameter(
                name="config",
                value='{"a": "1", "b": "2", "c": "3"}',
            )
        ],
    ),
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    annotations={"workflows.argoproj.io/version": ">= 3.1.0"},
    generate_name="expression-destructure-json-",
    entrypoint="main",
) as w:
    Script(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="a",
                    value="{{=jsonpath(workflow.parameters.config, '$.a')}}",
                ),
                Parameter(
                    name="b",
                    value="{{=jsonpath(workflow.parameters.config, '$.b')}}",
                ),
                Parameter(
                    name="c",
                    value="{{=jsonpath(workflow.parameters.config, '$.c')}}",
                ),
            ],
        ),
        name="main",
        command=["bash"],
        env=[
            EnvVar(
                name="A",
                value="{{inputs.parameters.a}}",
            ),
            EnvVar(
                name="B",
                value="{{inputs.parameters.b}}",
            ),
            EnvVar(
                name="C",
                value="{{inputs.parameters.c}}",
            ),
        ],
        image="debian:9.4",
        source='echo "$A$B$C"\n',
    )
