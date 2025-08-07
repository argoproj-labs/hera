"""This is an upstream example that only appears in the docs.

See https://argo-workflows.readthedocs.io/en/latest/walk-through/volumes/"""

from hera.workflows import (
    Container,
    ExistingVolume,
    Parameter,
    Resource,
    Step,
    Steps,
    Workflow,
)

with Workflow(
    generate_name="template-level-volume-",
    entrypoint="generate-and-use-volume",
) as w:
    generate_volume = Resource(
        name="generate-volume",
        inputs=[Parameter(name="pvc-size")],
        outputs=[Parameter(name="pvc-name", value_from={"jsonPath": "{.metadata.name}"})],
        action="create",
        set_owner_reference=True,
        manifest="""apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  generateName: pvc-example-
spec:
  accessModes: ['ReadWriteOnce', 'ReadOnlyMany']
  resources:
    requests:
      storage: '{{inputs.parameters.pvc-size}}'
""",
    )
    whalesay = Container(
        name="whalesay",
        inputs=[Parameter(name="pvc-name")],
        volumes=[ExistingVolume(name="workdir", claim_name="{{inputs.parameters.pvc-name}}", mount_path="/mnt/vol")],
        image="argoproj/argosay:v2",
        command=["sh", "-c"],
        args=["echo generating message in volume; cowsay hello world | tee /mnt/vol/hello_world.txt"],
    )
    print_message = Container(
        name="print-message",
        inputs=[Parameter(name="pvc-name")],
        volumes=[ExistingVolume(name="workdir", claim_name="{{inputs.parameters.pvc-name}}", mount_path="/mnt/vol")],
        image="alpine:latest",
        command=["sh", "-c"],
        args=["echo getting message from volume; find /mnt/vol; cat /mnt/vol/hello_world.txt"],
    )
    with Steps(name="generate-and-use-volume") as s:
        generate_vol_step: Step = generate_volume(name="generate-volume", arguments={"pvc-size": "1Gi"})
        whalesay(name="generate", arguments=generate_vol_step.get_parameter("pvc-name"))
        print_message(name="print", arguments=generate_vol_step.get_parameter("pvc-name"))
