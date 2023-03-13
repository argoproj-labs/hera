from hera.workflows import (
    Container,
    GitArtifact,
    Workflow,
)

with Workflow(generate_name="input-artifact-git-", entrypoint="git-clone") as w:
    Container(
        name="git-clone",
        image="golang:1.10",
        command=["sh", "-c"],
        args=["git status && ls && cat VERSION"],
        working_dir="/src",
        inputs=[
            GitArtifact(
                name="argo-source",
                path="/src",
                repo="https://github.com/argoproj/argo-workflows.git",
                revision="v2.1.1",
            ),
        ],
    )
