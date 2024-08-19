from hera.workflows import Container, Steps, Volume, Workflow

with Workflow(generate_name="volumes-pvc-", entrypoint="volumes-pvc-example") as w:
    v = Volume(name="workdir", size="1Gi", mount_path="/mnt/vol")
    hello_world_to_file = Container(
        name="hello-world-to-file",
        image="busybox",
        command=["sh", "-c"],
        args=["echo generating message in volume; echo hello world | tee /mnt/vol/hello_world.txt"],
        volumes=v,
    )
    print_message_from_file = Container(
        name="print-message-from-file",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["echo getting message from volume; find /mnt/vol; cat /mnt/vol/hello_world.txt"],
        volumes=v,
    )
    with Steps(name="volumes-pvc-example") as s:
        hello_world_to_file(name="generate")
        print_message_from_file(name="print")
