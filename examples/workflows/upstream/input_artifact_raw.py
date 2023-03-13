from hera.workflows import Container, RawArtifact, Workflow

with Workflow(generate_name="input-artifact-raw-", entrypoint="raw-contents") as w:
    Container(
        name="raw-contents",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["cat /tmp/file"],
        inputs=[
            RawArtifact(
                name="myfile",
                path="/tmp/file",
                data="this is\nthe raw file\ncontents\n",
            )
        ],
    )
