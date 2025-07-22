from hera.workflows import Script, Workflow
from hera.workflows.models import Arguments, EnvVar, Inputs, Parameter

with Workflow(
    arguments=Arguments(
        parameters=[
            Parameter(
                name="config",
                value='{"employees": [{"name": "Baris", "age":43},{"name": "Mo", "age": 42}, {"name": "Jai", "age" :44}]}',
            )
        ],
    ),
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="expression-destructure-json-complex-",
    entrypoint="main",
) as w:
    Script(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="a",
                    value="{{=jsonpath(workflow.parameters.config, '$.employees[?(@.name==\"Baris\")].age')}}",
                ),
                Parameter(
                    name="b",
                    value="{{=jsonpath(workflow.parameters.config, '$.employees[?(@.age>42 && @.age<44)].age')}}",
                ),
                Parameter(
                    name="c",
                    value="{{=jsonpath(workflow.parameters.config, '$.employees[0:1]')}}",
                ),
                Parameter(
                    name="d",
                    value="{{=jsonpath(workflow.parameters.config, '$.employees[*].name')}}",
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
            EnvVar(
                name="D",
                value="{{inputs.parameters.d}}",
            ),
        ],
        image="debian:9.4",
        source='echo "$A$B$C$D"\n',
    )
