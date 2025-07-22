from hera.workflows import Container, Data, Step, Steps, Workflow
from hera.workflows.models import (
    Arguments,
    Artifact,
    ArtifactPaths,
    DataSource,
    Inputs,
    Outputs,
    Parameter,
    S3Artifact,
)

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    annotations={
        "workflows.argoproj.io/description": "This workflow demonstrates using a data template to list in an S3 bucket\nand then process those log files.\n",
        "workflows.argoproj.io/version": ">= 3.1.0",
    },
    generate_name="data-transformations-",
    entrypoint="data-transformations",
) as w:
    with Steps(
        name="data-transformations",
    ) as invocator:
        Step(
            name="list-log-files",
            template="list-log-files",
        )
        Step(
            with_param="{{steps.list-log-files.outputs.result}}",
            arguments=Arguments(
                artifacts=[
                    Artifact(
                        name="file",
                        s3=S3Artifact(
                            key="{{item}}",
                        ),
                    )
                ],
                parameters=[
                    Parameter(
                        name="file-name",
                        value="{{item}}",
                    )
                ],
            ),
            name="process-logs",
            template="process-logs",
        )
    Data(
        name="list-log-files",
        outputs=Outputs(
            artifacts=[
                Artifact(
                    name="file",
                    path="/file",
                )
            ],
        ),
        source=DataSource(
            artifact_paths=ArtifactPaths(
                name="test-bucket",
                s3=S3Artifact(
                    bucket="my-bucket",
                ),
            ),
        ),
    )
    Container(
        inputs=Inputs(
            artifacts=[
                Artifact(
                    name="file",
                    path="/file",
                )
            ],
            parameters=[
                Parameter(
                    name="file-name",
                )
            ],
        ),
        name="process-logs",
        args=["echo {{inputs.parameters.file-name}}\nhead /file\n"],
        command=["sh", "-c"],
        image="argoproj/argosay:v2",
    )
