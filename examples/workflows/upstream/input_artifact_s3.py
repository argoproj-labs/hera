from hera.workflows import (
    Container,
    S3Artifact,
    Workflow,
    models as m,
)

with Workflow(generate_name="input-artifact-s3-", entrypoint="input-artifact-s3-example") as w:
    Container(
        name="input-artifact-s3-example",
        image="debian:latest",
        command=["sh", "-c"],
        args=["ls -l /my-artifact"],
        inputs=[
            S3Artifact(
                name="my-art",
                path="/my-artifact",
                endpoint="s3.amazonaws.com",
                bucket="my-bucket-name",
                key="path/in/bucket",
                region="us-west-2",
                access_key_secret=m.SecretKeySelector(
                    name="my-s3-credentials",
                    key="accessKey",
                ),
                secret_key_secret=m.SecretKeySelector(
                    name="my-s3-credentials",
                    key="secretKey",
                ),
            ),
        ],
    )
