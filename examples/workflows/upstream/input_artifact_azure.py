from hera.workflows import (
    AzureArtifact,
    Container,
    Workflow,
    models as m,
)

# the example is accidentally named input-artifact-s3-... upstream, keeping here for testing/consistency. Note that
# the Azure artifact is set correctly
with Workflow(generate_name="input-artifact-s3-", entrypoint="input-artifact-s3-example") as w:
    Container(
        name="input-artifact-s3-example",
        image="debian:latest",
        command=["sh", "-c"],
        args=["ls -l /my-artifact"],
        inputs=[
            AzureArtifact(
                name="my-art",
                path="/my-artifact",
                endpoint="https://myazurestorageaccountname.blob.core.windows.net",
                container="my-container",
                blob="path/in/container",
                account_key_secret=m.SecretKeySelector(
                    name="my-azure-credentials",
                    key="accountKey",
                ),
            )
        ],
    )
