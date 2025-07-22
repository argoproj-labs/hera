# Fun With Gifs

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/fun-with-gifs.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow
    from hera.workflows.models import (
        Artifact,
        ObjectMeta,
        Outputs,
        PersistentVolumeClaim,
        PersistentVolumeClaimSpec,
        Quantity,
        VolumeMount,
        VolumeResourceRequirements,
    )

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="fun-with-gifs-",
        entrypoint="run-workflow",
        volume_claim_templates=[
            PersistentVolumeClaim(
                metadata=ObjectMeta(
                    name="workdir",
                ),
                spec=PersistentVolumeClaimSpec(
                    access_modes=["ReadWriteOnce"],
                    resources=VolumeResourceRequirements(
                        requests={
                            "storage": Quantity(
                                __root__="1Gi",
                            )
                        },
                    ),
                ),
            )
        ],
    ) as w:
        with Steps(
            name="run-workflow",
        ) as invocator:
            Step(
                name="step-1",
                template="create-output-dir",
            )
            Step(
                name="step-2",
                template="download-images",
            )
            Step(
                name="step-3",
                template="create-gif",
            )
            Step(
                name="step-4",
                template="black-and-white",
            )
            Step(
                name="step-5",
                template="combine-horizontal",
            )
            Step(
                name="step-6",
                template="combine-vertical",
            )
            Step(
                name="step-7",
                template="make-bigger",
            )
            Step(
                name="step-8",
                template="bundle-up",
            )
        Container(
            name="create-output-dir",
            command=["mkdir", "/mnt/data/output"],
            image="alpine:3.6",
            volume_mounts=[
                VolumeMount(
                    mount_path="/mnt/data",
                    name="workdir",
                )
            ],
        )
        Container(
            name="download-images",
            command=[
                "aws",
                "--no-sign-request",
                "s3",
                "cp",
                "--recursive",
                "s3://ax-public/cricket_gif_images",
                "/mnt/data/",
            ],
            image="mesosphere/aws-cli",
            volume_mounts=[
                VolumeMount(
                    mount_path="/mnt/data",
                    name="workdir",
                )
            ],
        )
        Container(
            name="create-gif",
            command=["convert", "-delay", "20", "-loop", "0", "/mnt/data/*.gif", "/mnt/data/output/orig.gif"],
            image="v4tech/imagemagick",
            volume_mounts=[
                VolumeMount(
                    mount_path="/mnt/data",
                    name="workdir",
                )
            ],
        )
        Container(
            name="black-and-white",
            command=["convert", "/mnt/data/output/orig.gif", "-colorspace", "Gray", "/mnt/data/output/black_white.gif"],
            image="v4tech/imagemagick",
            volume_mounts=[
                VolumeMount(
                    mount_path="/mnt/data",
                    name="workdir",
                )
            ],
        )
        Container(
            name="combine-horizontal",
            command=["convert", "+append", "/mnt/data/*.gif", "/mnt/data/output/horizontal.gif"],
            image="v4tech/imagemagick",
            volume_mounts=[
                VolumeMount(
                    mount_path="/mnt/data",
                    name="workdir",
                )
            ],
        )
        Container(
            name="combine-vertical",
            command=["convert", "-append", "/mnt/data/*.gif", "/mnt/data/output/vertical.gif"],
            image="v4tech/imagemagick",
            volume_mounts=[
                VolumeMount(
                    mount_path="/mnt/data",
                    name="workdir",
                )
            ],
        )
        Container(
            name="make-bigger",
            command=[
                "gifsicle",
                "/mnt/data/output/orig.gif",
                "--resize",
                "1000x800",
                "-o",
                "/mnt/data/output/orig_big.gif",
            ],
            image="starefossen/gifsicle",
            volume_mounts=[
                VolumeMount(
                    mount_path="/mnt/data",
                    name="workdir",
                )
            ],
        )
        Container(
            name="bundle-up",
            outputs=Outputs(
                artifacts=[
                    Artifact(
                        name="output-gif",
                        path="/mnt/data/output",
                    )
                ],
            ),
            command=["ls"],
            image="alpine:3.6",
            volume_mounts=[
                VolumeMount(
                    mount_path="/mnt/data",
                    name="workdir",
                )
            ],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: fun-with-gifs-
    spec:
      entrypoint: run-workflow
      templates:
      - name: run-workflow
        steps:
        - - name: step-1
            template: create-output-dir
        - - name: step-2
            template: download-images
        - - name: step-3
            template: create-gif
        - - name: step-4
            template: black-and-white
        - - name: step-5
            template: combine-horizontal
        - - name: step-6
            template: combine-vertical
        - - name: step-7
            template: make-bigger
        - - name: step-8
            template: bundle-up
      - name: create-output-dir
        container:
          image: alpine:3.6
          command:
          - mkdir
          - /mnt/data/output
          volumeMounts:
          - name: workdir
            mountPath: /mnt/data
      - name: download-images
        container:
          image: mesosphere/aws-cli
          command:
          - aws
          - --no-sign-request
          - s3
          - cp
          - --recursive
          - s3://ax-public/cricket_gif_images
          - /mnt/data/
          volumeMounts:
          - name: workdir
            mountPath: /mnt/data
      - name: create-gif
        container:
          image: v4tech/imagemagick
          command:
          - convert
          - -delay
          - '20'
          - -loop
          - '0'
          - /mnt/data/*.gif
          - /mnt/data/output/orig.gif
          volumeMounts:
          - name: workdir
            mountPath: /mnt/data
      - name: black-and-white
        container:
          image: v4tech/imagemagick
          command:
          - convert
          - /mnt/data/output/orig.gif
          - -colorspace
          - Gray
          - /mnt/data/output/black_white.gif
          volumeMounts:
          - name: workdir
            mountPath: /mnt/data
      - name: combine-horizontal
        container:
          image: v4tech/imagemagick
          command:
          - convert
          - +append
          - /mnt/data/*.gif
          - /mnt/data/output/horizontal.gif
          volumeMounts:
          - name: workdir
            mountPath: /mnt/data
      - name: combine-vertical
        container:
          image: v4tech/imagemagick
          command:
          - convert
          - -append
          - /mnt/data/*.gif
          - /mnt/data/output/vertical.gif
          volumeMounts:
          - name: workdir
            mountPath: /mnt/data
      - name: make-bigger
        container:
          image: starefossen/gifsicle
          command:
          - gifsicle
          - /mnt/data/output/orig.gif
          - --resize
          - 1000x800
          - -o
          - /mnt/data/output/orig_big.gif
          volumeMounts:
          - name: workdir
            mountPath: /mnt/data
      - name: bundle-up
        container:
          image: alpine:3.6
          command:
          - ls
          volumeMounts:
          - name: workdir
            mountPath: /mnt/data
        outputs:
          artifacts:
          - name: output-gif
            path: /mnt/data/output
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

