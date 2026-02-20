"""Regression test: compare the new Annotated style inputs declaration with the old version."""

from typing import Annotated

from hera.shared import global_config
from hera.workflows import (
    Workflow,
    models as m,
    script,
)
from hera.workflows.artifact import Artifact, OSSArtifact
from hera.workflows.steps import Steps

global_config.experimental_features["script_annotations"] = True


@script()
def read_artifact(
    my_artifact: Annotated[
        str,
        OSSArtifact(
            name="my_artifact",
            path="/tmp/file",
            access_key_secret=m.SecretKeySelector(name="my-oss-credentials", key="secretKey"),
            bucket="test-bucket-name",
            create_bucket_if_not_present=True,
            endpoint="http://oss-cn-hangzhou-zmf.aliyuncs.com",
            key="test/mydirectory/",
            lifecycle_rule=m.OSSLifecycleRule(mark_deletion_after_days=42),
            secret_key_secret=m.SecretKeySelector(name="my-oss-credentials", key="secretKey"),
            security_token="oss-token",
        ),
    ],
) -> str:
    return my_artifact


with Workflow(generate_name="test-artifacts-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        read_artifact(arguments=[Artifact(name="my_artifact", from_="somewhere")])
