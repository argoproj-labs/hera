from hera.workflows import Container, Step, Steps, Workflow
from hera.workflows.models import Arguments, Inputs, Parameter

with Workflow(
    arguments=Arguments(
        parameters=[
            Parameter(
                name="os-list",
                value='[\n  { "image": "debian", "tag": "9.1" },\n  { "image": "debian", "tag": "8.9" },\n  { "image": "alpine", "tag": "3.6" },\n  { "image": "ubuntu", "tag": "17.10" }\n]\n',
            )
        ],
    ),
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="loops-param-arg-",
    entrypoint="loop-param-arg-example",
) as w:
    with Steps(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="os-list",
                )
            ],
        ),
        name="loop-param-arg-example",
    ) as invocator:
        Step(
            with_param="{{inputs.parameters.os-list}}",
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="image",
                        value="{{item.image}}",
                    ),
                    Parameter(
                        name="tag",
                        value="{{item.tag}}",
                    ),
                ],
            ),
            name="test-linux",
            template="cat-os-release",
        )
    Container(
        name="cat-os-release",
        annotations={"workflows.argoproj.io/display-name": "os-{{inputs.parameters.image}}-{{inputs.parameters.tag}}"},
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="image",
                ),
                Parameter(
                    name="tag",
                ),
            ],
        ),
        args=["/etc/os-release"],
        command=["cat"],
        image="{{inputs.parameters.image}}:{{inputs.parameters.tag}}",
    )
