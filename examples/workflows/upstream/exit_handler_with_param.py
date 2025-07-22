from hera.workflows import Container, Script, Step, Steps, Workflow
from hera.workflows.models import Arguments, Inputs, LifecycleHook, Outputs, Parameter, ValueFrom

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    annotations={
        "workflows.argoproj.io/description": "onExitTemplate enables workflow to pass the arguments (parameters/Artifacts) to exit handler template.\n",
        "workflows.argoproj.io/version": ">= 3.1.0",
    },
    generate_name="exit-handler-with-param-",
    labels={"workflows.argoproj.io/test": "true"},
    entrypoint="main",
) as w:
    with Steps(
        name="main",
    ) as invocator:
        Step(
            name="step-1",
            hooks={
                "exit": LifecycleHook(
                    arguments=Arguments(
                        parameters=[
                            Parameter(
                                name="message",
                                value="{{steps.step-1.outputs.parameters.result}}",
                            )
                        ],
                    ),
                    template="exit",
                )
            },
            template="output",
        )
    Container(
        name="output",
        outputs=Outputs(
            parameters=[
                Parameter(
                    name="result",
                    value_from=ValueFrom(
                        default="Foobar",
                        path="/tmp/hello_world.txt",
                    ),
                )
            ],
        ),
        args=["echo -n hello world > /tmp/hello_world.txt"],
        command=["sh", "-c"],
        image="python:alpine3.6",
    )
    Script(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="message",
                )
            ],
        ),
        name="exit",
        command=["python"],
        image="python:alpine3.6",
        source='print("{{inputs.parameters.message}}")',
    )
