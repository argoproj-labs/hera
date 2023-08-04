from hera.shared import global_config
from hera.workflows import Workflow, script
from hera.workflows.artifact import Artifact, OSSArtifact
from hera.workflows.steps import Steps

global_config.experimental_features["script_annotations"] = True


@script(
    inputs=[
        OSSArtifact(
            name="my_artifact",
            path="tmp/file",
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


with Workflow(generate_name="test-types-", entrypoint="my_steps") as w:
    with Steps(name="my_steps") as s:
        read_artifact(arguments=[Artifact(name="my_artifact", from_="somewhere")])
