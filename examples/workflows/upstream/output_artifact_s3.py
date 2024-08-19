from hera.workflows import (
    Container,
    S3Artifact,
    Workflow,
    models as m,
)

with Workflow(generate_name="output-artifact-s3-", entrypoint="hello-world-to-file") as w:
    Container(
        name="hello-world-to-file",
        image="busybox",
        command=["sh", "-c"],
        args=["echo hello world | tee /tmp/hello_world.txt"],
        outputs=[
            S3Artifact(
                name="message",
                path="/tmp",
                endpoint="s3.amazonaws.com",
                bucket="my-bucket",
                region="us-west-2",
                key="path/in/bucket/hello_world.txt.tgz",
                access_key_secret=m.SecretKeySelector(
                    name="my-s3-credentials",
                    key="accessKey",
                ),
                secret_key_secret=m.SecretKeySelector(
                    name="my-s3-credentials",
                    key="secretKey",
                ),
            )
        ],
    )
