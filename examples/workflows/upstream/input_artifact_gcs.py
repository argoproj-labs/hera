from hera.workflows import (
    Container,
    GCSArtifact,
    Workflow,
    models as m,
)

with Workflow(generate_name="input-artifact-gcs-", entrypoint="input-artifact-gcs-example") as w:
    Container(
        name="input-artifact-gcs-example",
        image="debian:latest",
        command=["sh", "-c"],
        args=["ls -l /my-artifact"],
        inputs=[
            GCSArtifact(
                name="my-art",
                path="/my-artifact",
                bucket="my-bucket-name",
                key="path/in/bucket",
                service_account_key_secret=m.SecretKeySelector(
                    name="my-gcs-credentials",
                    key="serviceAccountKey",
                ),
            ),
        ],
    )
