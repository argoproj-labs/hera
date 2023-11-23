"""This example showcases how to create a volume at a workflow level and use it in a container via a mount."""
from hera.workflows import Container, SecretVolume, Steps, Volume, Workflow
from hera.workflows.models import VolumeMount

with Workflow(
    generate_name="test-",
    volumes=[SecretVolume(name="service-account-credential", secret_name="service-account-credential")],
    entrypoint="test",
) as w:
    v_tmp_pod = Volume(
        name="tmp-pod",
        size="100Mi",
        mount_path="/tmp/pod",
    )
    init_container_example = Container(
        name="git-sync",
        volume_mounts=[VolumeMount(name="service-account-credential", mount_path="/secrets")],
        volumes=[v_tmp_pod],
    )
    with Steps(name="test") as s:
        init_container_example()
