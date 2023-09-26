# Volumes Emptydir

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/volumes-emptydir.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Container,
        Workflow,
        EmptyDirVolume,
        models as m,
    )

    with Workflow(
        generate_name="volumes-emptydir-",
        entrypoint="volumes-emptydir-example",
        volumes=[EmptyDirVolume(name="workdir")],
    ) as w:
        empty_dir = Container(
            name="volumes-emptydir-example",
            image="debian:latest",
            command=["/bin/bash", "-c"],
            args=[
                (
                    " vol_found=`mount | grep /mnt/vol` && "
                    + 'if [[ -n $vol_found ]]; then echo "Volume mounted and found"; else echo "Not found"; fi '
                )
            ],
            volume_mounts=[m.VolumeMount(name="workdir", mount_path="/mnt/vol")],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: volumes-emptydir-
    spec:
      entrypoint: volumes-emptydir-example
      templates:
      - container:
          args:
          - ' vol_found=`mount | grep /mnt/vol` && if [[ -n $vol_found ]]; then echo "Volume
            mounted and found"; else echo "Not found"; fi '
          command:
          - /bin/bash
          - -c
          image: debian:latest
          volumeMounts:
          - mountPath: /mnt/vol
            name: workdir
        name: volumes-emptydir-example
      volumes:
      - emptyDir: {}
        name: workdir
    ```

