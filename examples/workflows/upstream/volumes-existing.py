from hera.workflows import Container, Workflow, Steps, Step
from hera.workflows import models as m

with Workflow(
    generate_name="volumes-existing-",
    entrypoint="volumes-existing-example",
    volumes=[m.Volume(name="workdir", persistent_volume_claim={"claim_name": "my-existing-volume"})],
) as w:
    with Steps(name="volumes-existing-example") as s:
        Step(name="generate", template="append-to-accesslog")
        Step(name="print", template="print-accesslog")
    Container(
        name="append-to-accesslog",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["echo accessed at: $(date) | tee -a /mnt/vol/accesslog"],
        volume_mounts=[
            m.VolumeMount(name="workdir", mount_path="/mnt/vol"),
        ],
    )
    Container(
        name="print-accesslog",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["echo 'Volume access log:'; cat /mnt/vol/accesslog"],
        volume_mounts=[
            m.VolumeMount(name="workdir", mount_path="/mnt/vol"),
        ],
    )
