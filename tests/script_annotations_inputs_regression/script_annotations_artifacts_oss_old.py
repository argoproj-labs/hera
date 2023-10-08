"""Regression test: compare the new Annotated style inputs declaration with the old version."""

from hera.workflows import Workflow, script
from hera.workflows.artifact import Artifact, OSSArtifact
from hera.workflows.steps import Steps


@script(
    inputs=[
        OSSArtifact(
            name="my_artifact",
            path="/tmp/file",
            access_key_secret={"name": "my-oss-credentials", "key": "secretKey"},
            bucket="test-bucket-name",
            create_bucket_if_not_present=True,
            endpoint="http://oss-cn-hangzhou-zmf.aliyuncs.com",
            key="test/mydirectory/",
            lifecycle_rule={"name": "my-oss-rule", "key": "ruleKey"},
            secret_key_secret={"name": "my-oss-credentials", "key": "secretKey"},
            security_token="oss-token",
        ),
    ]
)
def read_artifact(my_artifact) -> str:
    return my_artifact


with Workflow(generate_name="test-artifacts-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        read_artifact(arguments=[Artifact(name="my_artifact", from_="somewhere")])
