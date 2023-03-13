from hera.workflows import (
    AzureArtifact,
    Container,
    Workflow,
    models as m,
)

with Workflow(generate_name="output-artifact-s3-", entrypoint="whalesay") as w:
    Container(
        name="whalesay",
        image="docker/whalesay:latest",
        command=["sh", "-c"],
        args=["cowsay hello world | tee /tmp/hello_world.txt"],
        outputs=[
            AzureArtifact(
                name="message",
                path="/tmp",
                endpoint="https://myazurestorageaccountname.blob.core.windows.net",
                container="my-container",
                blob="path/in/container/hello_world.txt.tgz",
                account_key_secret=m.SecretKeySelector(name="my-azure-credentials", key="accountKey"),
            )
        ],
    )
