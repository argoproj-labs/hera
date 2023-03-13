from hera.workflows import Container, HTTPArtifact, Workflow

with Workflow(generate_name="input-artifact-http-", entrypoint="http-artifact-example") as w:
    Container(
        name="http-artifact-example",
        image="debian:9.4",
        command=["sh", "-c"],
        args=["kubectl version"],
        inputs=[
            HTTPArtifact(
                name="kubectl",
                path="/bin/kubectl",
                mode=493,
                url="https://storage.googleapis.com/kubernetes-release/release/v1.8.0/bin/linux/amd64/kubectl",
            ),
        ],
    )
