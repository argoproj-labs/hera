# Volumes Pvc

> Note: This example is a replication of an Argo Workflow example in Hera. 




=== "Hera"

    ```python linenums="1"
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

