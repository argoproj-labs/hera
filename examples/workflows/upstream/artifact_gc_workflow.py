from hera.workflows import (
    Container,
    S3Artifact,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="artifact-gc-", entrypoint="main", artifact_gc=m.WorkflowLevelArtifactGC(strategy="OnWorkflowDeletion")
) as w:
    main = Container(
        name="main",
        image="argoproj/argosay:v2",
        command=["sh", "-c"],
        args=['echo "hello world" > /tmp/on-completion.txt\necho "hello world" > /tmp/on-deletion.txt\n'],
        outputs=[
            S3Artifact(
                name="on-completion",
                path="/tmp/on-completion.txt",
                key="on-completion.txt",
                artifact_gc=m.ArtifactGC(strategy="OnWorkflowCompletion"),
            ),
            S3Artifact(
                name="on-deletion",
                path="/tmp/on-deletion.txt",
                key="on-deletion.txt",
            ),
        ],
    )
