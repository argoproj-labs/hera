from hera.workflows import Container, Workflow, Steps, Step
from hera.workflows import models as m
from typing import List


def get_container(name: str, args: List[str]) -> Container:
    """Creates container (alpine:latest) with a mounted volume"""
    return Container(
        name=name,
        image="alpine:latest",
        command=["sh", "-c"],
        args=args,
        volume_mounts=[
            m.VolumeMount(name="workdir", mount_path="/mnt/vol"),
        ]
    )


with Workflow(
    generate_name="volumes-existing-",
    entrypoint="volumes-existing-example",
    volumes=[m.Volume(name="workdir", persistent_volume_claim={"claim_name": "my-existing-volume"})],
) as w:
    with Steps(name="volumes-existing-example") as s:
        Step(name="generate", template="append-to-accesslog")
        Step(name="print", template="print-accesslog")

    get_container("append-to-accesslog", ["echo accessed at: $(date) | tee -a /mnt/vol/accesslog"])
    get_container("print-accesslog", ["echo 'Volume access log:'; cat /mnt/vol/accesslog"])
