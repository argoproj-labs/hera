from hera.workflows import DAG, Container, Task, Workflow
from hera.workflows.models import Arguments, Inputs, Outputs, Parameter, ValueFrom

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    annotations={"workflows.argoproj.io/version": ">= 3.1.0"},
    generate_name="expression-tag-template-",
    labels={"workflows.argoproj.io/test": "true"},
    entrypoint="main",
) as w:
    with DAG(
        name="main",
    ) as invocator:
        Task(
            with_param="{{=toJson(filter([1, 3], {# > 1}))}}",
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="foo",
                        value="{{=item}}",
                    )
                ],
            ),
            name="task-0",
            template="pod-0",
        )
    Container(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="foo",
                )
            ],
        ),
        name="pod-0",
        outputs=Outputs(
            parameters=[
                Parameter(
                    name="output",
                    value_from=ValueFrom(
                        path="/output",
                    ),
                )
            ],
        ),
        args=[
            "echo",
            "hello {{=asInt(inputs.parameters.foo) * 10}} @ {{=sprig.date('2006', workflow.creationTimestamp)}}\n",
            "/output",
        ],
        image="argoproj/argosay:v2",
    )
