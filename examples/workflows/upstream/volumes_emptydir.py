from hera.workflows import (
    Container,
    EmptyDirVolume,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="volumes-emptydir-",
    entrypoint="volumes-emptydir-example",
    volumes=[EmptyDirVolume(name="workdir")],
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
        volume_mounts=[m.VolumeMount(name="workdir", mount_path="/mnt/vol")],
    )
