from hera.workflows import Artifact, Container, HTTPArtifact, Workflow

with Workflow(
    generate_name="arguments-artifacts-",
    entrypoint="kubectl-input-artifact",
    arguments=[
        HTTPArtifact(
            name="kubectl",
            url="https://storage.googleapis.com/kubernetes-release/release/v1.8.0/bin/linux/amd64/kubectl",
        ),
    ],
) as w:
    Container(
        name="kubectl-input-artifact",
        image="debian:9.4",
        command=["sh", "-c"],
        args=["kubectl version"],
        inputs=[Artifact(name="kubectl", path="/usr/local/bin/kubectl", mode=493)],
    )
