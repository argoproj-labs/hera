from hera.workflows import Script, Workflow
from hera.workflows.models import Arguments, EnvVar, Inputs, Parameter

with Workflow(
    arguments=Arguments(
        parameters=[
            Parameter(
                name="weather",
                value='{"weekWeather": "eyJ0ZW1wcyI6IFszNCwgMjcsIDE1LCA1NywgNDZdfQo="}',
            )
        ],
    ),
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="expression-reusing-verbose-snippets-",
    entrypoint="main",
) as w:
    Script(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="week-temps",
                    value="{{=\n  map([\n      jsonpath(sprig.b64dec(jsonpath(workflow.parameters.weather, '$.weekWeather')), '$.temps')\n    ], {\n      toJson({\n        avg: sprig.add(#[0], #[1], #[2], #[3], #[4]) / 5,\n        min: sprig.min(#[0], #[1], #[2], #[3], #[4]),\n        max: sprig.max(#[0], #[1], #[2], #[3], #[4])\n      })\n  })[0]\n}}",
                )
            ],
        ),
        name="main",
        command=["bash"],
        env=[
            EnvVar(
                name="AVG",
                value="{{=jsonpath(inputs.parameters['week-temps'], '$.avg')}}",
            ),
            EnvVar(
                name="MIN",
                value="{{=jsonpath(inputs.parameters['week-temps'], '$.min')}}",
            ),
            EnvVar(
                name="MAX",
                value="{{=jsonpath(inputs.parameters['week-temps'], '$.max')}}",
            ),
        ],
        image="debian:9.4",
        source='echo "The week\'s average temperature was $AVG with a minimum of $MIN and a maximum of $MAX."\n',
    )
