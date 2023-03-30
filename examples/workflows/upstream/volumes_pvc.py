from hera.workflows import Container, Steps, Volume, Workflow

with Workflow(generate_name="volumes-pvc-", entrypoint="volumes-pvc-example") as w:
    v = Volume(name="workdir", size="1Gi", mount_path="/mnt/vol")
    whalesay = Container(
        name="whalesay",
        image="docker/whalesay:latest",
        command=["sh", "-c"],
        args=["echo generating message in volume; cowsay hello world | tee /mnt/vol/hello_world.txt"],
        volumes=v,
    )
    print_message = Container(
        name="print-message",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["echo getting message from volume; find /mnt/vol; cat /mnt/vol/hello_world.txt"],
        volumes=v,
    )
    with Steps(name="volumes-pvc-example") as s:
        whalesay(name="generate")
        print_message(name="print")

print(w.to_yaml())
