from hera.workflows import Container, Workflow, Steps, Step
from hera.workflows import models as m
from typing import List


def get_container(name: str, image: str, args: List[str]) -> Container:
    """Creates container with a mounted volume"""
    return Container(
        name=name,
        image=image,
        command=["sh", "-c"],
        args=args,
        volume_mounts=[
            m.VolumeMount(name="workdir", mount_path="/mnt/vol"),
        ],
    )


with Workflow(
    generate_name="volumes-pvc-",
    entrypoint="volumes-pvc-example",
    volume_claim_templates=[
        m.PersistentVolumeClaim(
            metadata=m.ObjectMeta(name="workdir"),
            spec=m.PersistentVolumeClaimSpec(
                access_modes=["ReadWriteOnce"],
                resources=m.ResourceRequirements(
                    requests={
                        "storage": m.Quantity(__root__="1Gi"),
                    }
                ),
            ),
        )
    ],
) as w:
    whalesay = get_container(
        "whalesay",
        "docker/whalesay:latest",
        ["echo generating message in volume; cowsay hello world | tee /mnt/vol/hello_world.txt"],
    )
    print_message = get_container(
        "print-message",
        "alpine:latest",
        ["echo getting message from volume; find /mnt/vol; cat /mnt/vol/hello_world.txt"],
    )
    with Steps(name="volumes-pvc-example") as s:
        whalesay(name="generate")
        print_message(name="print")
