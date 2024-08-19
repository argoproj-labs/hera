# Volumes Pvc

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/volumes-pvc.yaml).




=== "Hera"

    ```python linenums="1"
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
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: volumes-pvc-
    spec:
      entrypoint: volumes-pvc-example
      templates:
      - container:
          args:
          - echo generating message in volume; echo hello world | tee /mnt/vol/hello_world.txt
          command:
          - sh
          - -c
          image: busybox
          volumeMounts:
          - mountPath: /mnt/vol
            name: workdir
        name: hello-world-to-file
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
        name: print-message-from-file
      - name: volumes-pvc-example
        steps:
        - - name: generate
            template: hello-world-to-file
        - - name: print
            template: print-message-from-file
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

