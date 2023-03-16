# Volumes Pvc

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/volumes-pvc.yaml).

apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: volumes-pvc-
spec:
  entrypoint: volumes-pvc-example
  volumeClaimTemplates:
  - metadata:
      name: workdir
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi

  templates:
  - name: volumes-pvc-example
    steps:
    - - name: generate
        template: whalesay
    - - name: print
        template: print-message

  - name: whalesay
    container:
      image: docker/whalesay:latest
      command: [sh, -c]
      args: ["echo generating message in volume; cowsay hello world | tee /mnt/vol/hello_world.txt"]
      volumeMounts:
      - name: workdir
        mountPath: /mnt/vol

  - name: print-message
    container:
      image: alpine:latest
      command: [sh, -c]
      args: ["echo getting message from volume; find /mnt/vol; cat /mnt/vol/hello_world.txt"]
      volumeMounts:
      - name: workdir
        mountPath: /mnt/vol

## Hera

```python
from hera.workflows import (
    Container,
    Steps,
    Volume,
    Workflow,
    models as m,
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
                    requests={"storage": m.Quantity(__root__="1Gi")},
                ),
            ),
        )
    ],
) as w:
    v = Volume(
        name="workdir",
        size="1Gi",
        mount_path="/mnt/vol",
        access_modes=["ReadWriteOnce"],
    )
    whalesay = Container(
        name="whalesay",
        image="docker/whalesay:latest",
        command=["sh", "-c"],
        args=["echo generating message in volume; cowsay hello world | tee /mnt/vol/hello_world.txt"],
        volume_mounts=[m.VolumeMount(name="workdir", mount_path="/mnt/vol")],
    )
    print_message = Container(
        name="print-message",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["echo getting message from volume; find /mnt/vol; cat /mnt/vol/hello_world.txt"],
        volume_mounts=[m.VolumeMount(name="workdir", mount_path="/mnt/vol")],
    )
    with Steps(name="volumes-pvc-example") as s:
        whalesay(name="generate")
        print_message(name="print")
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: volumes-pvc-
spec:
  entrypoint: volumes-pvc-example
  templates:
  - container:
      args:
      - echo generating message in volume; cowsay hello world | tee /mnt/vol/hello_world.txt
      command:
      - sh
      - -c
      image: docker/whalesay:latest
      volumeMounts:
      - mountPath: /mnt/vol
        name: workdir
    name: whalesay
  - container:
      args:
      - echo getting message from volume; find /mnt/vol; cat /mnt/vol/hello_world.txt
      command:
      - sh
      - -c
      image: alpine:latest
      volumeMounts:
      - mountPath: /mnt/vol
        name: workdir
    name: print-message
  - name: volumes-pvc-example
    steps:
    - - name: generate
        template: whalesay
    - - name: print
        template: print-message
  volumeClaimTemplates:
  - metadata:
      name: workdir
    spec:
      accessModes:
      - ReadWriteOnce
      resources:
        requests:
          storage: 1Gi
```
