from hera.workflows import Container, Workflow, Steps, Step
from hera.workflows import models as m

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
    with Steps(name="volumes-pvc-example") as s:
        Step(name="generate", template="whalesay")
        Step(name="print", template="print-message")
    Container(
        name="whalesay",
        image="docker/whalesay:latest",
        command=["sh", "-c"],
        args=["echo generating message in volume; cowsay hello world | tee /mnt/vol/hello_world.txt"],
        volume_mounts=[
            m.VolumeMount(name="workdir", mount_path="/mnt/vol"),
        ],
    )
    Container(
        name="print-message",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["echo getting message from volume; find /mnt/vol; cat /mnt/vol/hello_world.txt"],
        volume_mounts=[
            m.VolumeMount(name="workdir", mount_path="/mnt/vol"),
        ],
    )
