from hera.workflows import Container, Workflow
from hera.workflows.models import EnvVar, EnvVarSource, SecretKeySelector, SecretVolumeSource, Volume, VolumeMount

with Workflow(
    volumes=[
        Volume(
            name="my-secret-vol",
            secret=SecretVolumeSource(
                secret_name="my-secret",
            ),
        )
    ],
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="secrets-",
    entrypoint="print-secret",
) as w:
    Container(
        name="print-secret",
        args=[
            ' echo "secret from env: $MYSECRETPASSWORD"; echo "secret from file: `cat /secret/mountpath/mypassword`" '
        ],
        command=["sh", "-c"],
        env=[
            EnvVar(
                name="MYSECRETPASSWORD",
                value_from=EnvVarSource(
                    secret_key_ref=SecretKeySelector(
                        key="mypassword",
                        name="my-secret",
                    ),
                ),
            )
        ],
        image="alpine:3.7",
        volume_mounts=[
            VolumeMount(
                mount_path="/secret/mountpath",
                name="my-secret-vol",
            )
        ],
    )
