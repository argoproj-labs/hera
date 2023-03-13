from hera.workflows import (
    Container,
    OSSArtifact,
    Workflow,
    models as m,
)

with Workflow(generate_name="input-artifact-oss-", entrypoint="input-artifact-oss-example") as w:
    Container(
        name="input-artifact-oss-example",
        image="debian:latest",
        command=["sh", "-c"],
        args=["ls -l /my-artifact"],
        inputs=[
            OSSArtifact(
                name="my-art",
                path="/my-artifact",
                endpoint="http://oss-cn-hangzhou-zmf.aliyuncs.com",
                bucket="test-bucket-name",
                key="test/mydirectory/",
                access_key_secret=m.SecretKeySelector(
                    name="my-oss-credentials",
                    key="accessKey",
                ),
                secret_key_secret=m.SecretKeySelector(
                    name="my-oss-credentials",
                    key="secretKey",
                ),
            )
        ],
    )
