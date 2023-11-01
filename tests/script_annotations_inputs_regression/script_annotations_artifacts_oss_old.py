"""Regression test: compare the new Annotated style inputs declaration with the old version."""

from hera.workflows import (
    Artifact,
    OSSArtifact,
    Steps,
    Workflow,
    models as m,
    script,
)


@script(
    inputs=[
        OSSArtifact(
            name="my_artifact",
            path="/tmp/file",
            access_key_secret=m.SecretKeySelector(name="my-oss-credentials", key="secretKey"),
            secret_key_secret=m.SecretKeySelector(name="my-oss-credentials", key="secretKey"),
            bucket="test-bucket-name",
            create_bucket_if_not_present=True,
            endpoint="http://oss-cn-hangzhou-zmf.aliyuncs.com",
            key="test/mydirectory/",
            lifecycle_rule=m.OSSLifecycleRule(mark_deletion_after_days=42),
            security_token="oss-token",
        ),
    ]
)
def read_artifact(my_artifact) -> str:
    return my_artifact


with Workflow(generate_name="test-artifacts-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        read_artifact(arguments=[Artifact(name="my_artifact", from_="somewhere")])
