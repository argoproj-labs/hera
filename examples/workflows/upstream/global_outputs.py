from hera.workflows import Container, Step, Steps, Workflow
from hera.workflows.models import Arguments, Artifact, Inputs, Outputs, Parameter, ValueFrom

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="global-outputs-",
    entrypoint="generate-globals",
    on_exit="consume-globals",
) as w:
    with Steps(
        name="generate-globals",
    ) as invocator:
        Step(
            name="generate",
            template="global-output",
        )
        Step(
            name="consume-globals",
            template="consume-globals",
        )
    Container(
        name="global-output",
        outputs=Outputs(
            artifacts=[
                Artifact(
                    global_name="my-global-art",
                    name="hello-art",
                    path="/tmp/hello_world.txt",
                )
            ],
            parameters=[
                Parameter(
                    global_name="my-global-param",
                    name="hello-param",
                    value_from=ValueFrom(
                        path="/tmp/hello_world.txt",
                    ),
                )
            ],
        ),
        args=["sleep 1; echo -n hello world > /tmp/hello_world.txt"],
        command=["sh", "-c"],
        image="alpine:3.7",
    )
    with Steps(
        name="consume-globals",
    ) as invocator:
        with invocator.parallel():
            Step(
                name="consume-global-param",
                template="consume-global-param",
            )
            Step(
                arguments=Arguments(
                    artifacts=[
                        Artifact(
                            from_="{{workflow.outputs.artifacts.my-global-art}}",
                            name="art",
                        )
                    ],
                ),
                name="consume-global-art",
                template="consume-global-art",
            )
    Container(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="param",
                    value="{{workflow.outputs.parameters.my-global-param}}",
                )
            ],
        ),
        name="consume-global-param",
        args=["echo {{inputs.parameters.param}}"],
        command=["sh", "-c"],
        image="alpine:3.7",
    )
    Container(
        inputs=Inputs(
            artifacts=[
                Artifact(
                    name="art",
                    path="/art",
                )
            ],
        ),
        name="consume-global-art",
        args=["cat /art"],
        command=["sh", "-c"],
        image="alpine:3.7",
    )
