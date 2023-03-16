from hera.workflows import Container, Workflow
from hera.workflows.models import EmptyDirVolumeSource, Volume, VolumeMount

with Workflow(
    generate_name="volumes-emptydir-",
    entrypoint="volumes-emptydir-example",
    volumes=[Volume(name="workdir", empty_dir=EmptyDirVolumeSource())],
) as w:
    empty_dir = Container(
        name="volumes-emptydir-example",
        image="debian:latest",
        command=["/bin/bash", "-c"],
        args=[
            (
                " vol_found=`mount | grep /mnt/vol` && "
                + 'if [[ -n $vol_found ]]; then echo "Volume mounted and found"; else echo "Not found"; fi '
            )
        ],
        volume_mounts=[VolumeMount(name="workdir", mount_path="/mnt/vol")],
    )
