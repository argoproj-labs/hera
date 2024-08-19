from hera.workflows import (
    Container,
    GCSArtifact,
    Workflow,
    models as m,
)

with Workflow(generate_name="output-artifact-gcs-", entrypoint="hello-world-to-file") as w:
    Container(
        name="hello-world-to-file",
        image="busybox",
        command=["sh", "-c"],
        args=["echo hello world | tee /tmp/hello_world.txt"],
        outputs=[
            GCSArtifact(
                name="message",
                path="/tmp",
                bucket="my-bucket",
                key="path/in/bucket/hello_world.txt.tgz",
                service_account_key_secret=m.SecretKeySelector(name="my-gcs-credentials", key="serviceAccountKey"),
            )
        ],
    )
