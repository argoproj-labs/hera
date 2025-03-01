# Template Level Volume



This is an upstream example that only appears in the docs.

See https://argo-workflows.readthedocs.io/en/latest/walk-through/volumes/


=== "Hera"

    ```python linenums="1"
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
            image="docker/whalesay:latest",
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
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: template-level-volume-
    spec:
      entrypoint: generate-and-use-volume
      templates:
      - name: generate-volume
        inputs:
          parameters:
          - name: pvc-size
        outputs:
          parameters:
          - name: pvc-name
            valueFrom:
              jsonPath: '{.metadata.name}'
        resource:
          action: create
          manifest: |
            apiVersion: v1
            kind: PersistentVolumeClaim
            metadata:
              generateName: pvc-example-
            spec:
              accessModes: ['ReadWriteOnce', 'ReadOnlyMany']
              resources:
                requests:
                  storage: '{{inputs.parameters.pvc-size}}'
          setOwnerReference: true
      - name: whalesay
        volumes:
        - name: workdir
          persistentVolumeClaim:
            claimName: '{{inputs.parameters.pvc-name}}'
        container:
          image: docker/whalesay:latest
          args:
          - echo generating message in volume; cowsay hello world | tee /mnt/vol/hello_world.txt
          command:
          - sh
          - -c
          volumeMounts:
          - name: workdir
            mountPath: /mnt/vol
        inputs:
          parameters:
          - name: pvc-name
      - name: print-message
        volumes:
        - name: workdir
          persistentVolumeClaim:
            claimName: '{{inputs.parameters.pvc-name}}'
        container:
          image: alpine:latest
          args:
          - echo getting message from volume; find /mnt/vol; cat /mnt/vol/hello_world.txt
          command:
          - sh
          - -c
          volumeMounts:
          - name: workdir
            mountPath: /mnt/vol
        inputs:
          parameters:
          - name: pvc-name
      - name: generate-and-use-volume
        steps:
        - - arguments:
              parameters:
              - name: pvc-size
                value: 1Gi
            name: generate-volume
            template: generate-volume
        - - arguments:
              parameters:
              - name: pvc-name
                value: '{{steps.generate-volume.outputs.parameters.pvc-name}}'
            name: generate
            template: whalesay
        - - arguments:
              parameters:
              - name: pvc-name
                value: '{{steps.generate-volume.outputs.parameters.pvc-name}}'
            name: print
            template: print-message
    ```

