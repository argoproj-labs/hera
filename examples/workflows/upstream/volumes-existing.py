from typing import List

from hera.workflows import (
    Container,
    Steps,
    Workflow,
    models as m,
)


def get_container(name: str, args: List[str]) -> Container:
    """Creates container (alpine:latest) with a mounted volume"""
    return Container(
        name=name,
        image="alpine:latest",
        command=["sh", "-c"],
        args=args,
        volume_mounts=[
            m.VolumeMount(name="workdir", mount_path="/mnt/vol"),
        ],
    )


with Workflow(
    generate_name="volumes-existing-",
    entrypoint="volumes-existing-example",
    volumes=[m.Volume(name="workdir", persistent_volume_claim={"claim_name": "my-existing-volume"})],
) as w:
    append_to_log = get_container("append-to-accesslog", ["echo accessed at: $(date) | tee -a /mnt/vol/accesslog"])
    print_log = get_container("print-accesslog", ["echo 'Volume access log:'; cat /mnt/vol/accesslog"])

    with Steps(name="volumes-existing-example") as s:
        append_to_log(name="generate")
        print_log(name="print")
