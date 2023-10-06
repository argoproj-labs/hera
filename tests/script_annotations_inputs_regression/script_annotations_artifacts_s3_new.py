"""Regression test: compare the new Annotated style inputs declaration with the old version."""

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

from hera.shared import global_config
from hera.workflows import Workflow, script
from hera.workflows.artifact import Artifact, S3Artifact
from hera.workflows.steps import Steps

global_config.experimental_features["script_annotations"] = True


@script()
def read_artifact(
    my_artifact: Annotated[
        str,
        S3Artifact(
            name="my_artifact",
            path="/tmp/file",
            access_key_secret={"name": "my-oss-credentials", "key": "secretKey"},
            bucket="my-bucket-name",
            create_bucket_if_not_present={"value": "true"},
            encryption_options={"value": "s3-encryption"},
            endpoint="s3.amazonaws.com",
            insecure=True,
            key="path/in/bucket",
            region="us-west-2",
            role_arn="s3-role-arn",
            secret_key_secret={"name": "my-oss-credentials", "key": "secretKey"},
            use_sdk_creds=True,
        ),
    ]
) -> str:
    return my_artifact


with Workflow(generate_name="test-artifacts-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        read_artifact(arguments=[Artifact(name="my_artifact", from_="somewhere")])
