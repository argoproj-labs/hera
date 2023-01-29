# Artifact-Disable-Archive

This example showcases the ability to disable archiving.

https://github.com/argoproj/argo-workflows/blob/master/examples/artifact-disable-archive.yaml

```python
from hera import Service
from hera.models import (
    ArchiveStrategy,
    Arguments,
    Artifact,
    Container,
    NoneStrategy,
    ObjectMeta,
    Outputs,
    ParallelSteps,
    TarStrategy,
    Template,
    Workflow,
    WorkflowCreateRequest,
    WorkflowSpec,
    WorkflowStep,
)

workflow = Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    metadata=ObjectMeta(generate_name="artifact-disable-archive-"),
    spec=WorkflowSpec(
        entrypoint="artifact-disable-archive",
        templates=[
            Template(
                name="artifact-disable-archive",
                steps=[
                    ParallelSteps(
                        __root__=[
                            WorkflowStep(name="generate-artifact", template="whalesay"),
                            WorkflowStep(
                                name="consume-artifact",
                                template="print-message",
                                arguments=Arguments(
                                    artifacts=[
                                        Artifact(
                                            name="etc",
                                            from_="{{steps.generate-artifact.outputs.artifacts.etc}}",
                                        ),
                                        Artifact(
                                            name="hello-txt",
                                            from_="{{steps.generate-artifact.outputs.artifacts.hello-txt}}",
                                        ),
                                        Artifact(
                                            name="hello-txt-nc",
                                            from_="{{steps.generate-artifact.outputs.artifacts.hello-txt-nc}}",
                                        ),
                                    ]
                                ),
                            ),
                        ]
                    )
                ],
            ),
            Template(
                name="whalesay",
                container=Container(
                    image="docker/whalesay:latest",
                    command=["sh", "-c"],
                    args=["cowsay hello world | tee /tmp/hello_world.txt | tee /tmp/hello_world_nc.txt ; sleep 1"],
                ),
                outputs=Outputs(
                    artifacts=[
                        Artifact(name="etc", path="/etc", archive=ArchiveStrategy(none=NoneStrategy())),
                        Artifact(
                            name="hello-txt", path="/tmp/hello_world.txt", archive=ArchiveStrategy(none=NoneStrategy())
                        ),
                        Artifact(
                            name="hello-txt-nc",
                            path="/tmp/hello_world_nc.txt",
                            archive=ArchiveStrategy(tar=TarStrategy(compression_level=0)),
                        ),
                    ]
                ),
            ),
        ],
    ),
)

Service().create_workflow("argo", WorkflowCreateRequest(workflow=workflow))
```
