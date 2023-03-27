# Volumes Existing

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/volumes-existing.yaml).




=== "Hera"

    ```python linenums="1"
    from typing import List

    from hera.workflows import (
        Container,
        Steps,
        Workflow,
        models as m,
    )


    def _get_container(name: str, args: List[str]) -> Container:
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
        append_to_log = _get_container("append-to-accesslog", ["echo accessed at: $(date) | tee -a /mnt/vol/accesslog"])
        print_log = _get_container("print-accesslog", ["echo 'Volume access log:'; cat /mnt/vol/accesslog"])

        with Steps(name="volumes-existing-example") as s:
            append_to_log(name="generate")
            print_log(name="print")
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: volumes-existing-
    spec:
      entrypoint: volumes-existing-example
      templates:
      - container:
          args:
          - 'echo accessed at: $(date) | tee -a /mnt/vol/accesslog'
          command:
          - sh
          - -c
          image: alpine:latest
          volumeMounts:
          - mountPath: /mnt/vol
            name: workdir
        name: append-to-accesslog
      - container:
          args:
          - echo 'Volume access log:'; cat /mnt/vol/accesslog
          command:
          - sh
          - -c
          image: alpine:latest
          volumeMounts:
          - mountPath: /mnt/vol
            name: workdir
        name: print-accesslog
      - name: volumes-existing-example
        steps:
        - - name: generate
            template: append-to-accesslog
        - - name: print
            template: print-accesslog
      volumes:
      - name: workdir
        persistentVolumeClaim:
          claimName: my-existing-volume
    ```

