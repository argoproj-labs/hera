# Volumes-Pvc

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/volumes-pvc.yaml).



## Hera

```python
from typing import List

from hera.workflows import (
    Container,
    Steps,
    Workflow,
    models as m,
)


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
