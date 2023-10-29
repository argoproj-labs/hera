"""Regression test: compare the new Annotated style inputs declaration with the old version."""

from hera.workflows import (
    Artifact,
    S3Artifact,
    Steps,
    Workflow,
    models as m,
    script,
)


@script(
    inputs=[
        S3Artifact(
            name="my_artifact",
            path="/tmp/file",
            access_key_secret=m.SecretKeySelector(name="my-oss-credentials", key="secretKey"),
            bucket="my-bucket-name",
            create_bucket_if_not_present=m.CreateS3BucketOptions(object_locking=True),
            encryption_options=m.S3EncryptionOptions(enable_encryption=True),
            endpoint="s3.amazonaws.com",
            insecure=True,
            key="path/in/bucket",
            region="us-west-2",
            role_arn="s3-role-arn",
            secret_key_secret=m.SecretKeySelector(name="my-oss-credentials", key="secretKey"),
            use_sdk_creds=True,
        ),
    ]
)
def read_artifact(my_artifact) -> str:
    return my_artifact


with Workflow(generate_name="test-artifacts-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        read_artifact(arguments=[Artifact(name="my_artifact", from_="somewhere")])
