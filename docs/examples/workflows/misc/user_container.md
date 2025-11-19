# User Container



This example showcases the user of a user container with a volume mount.


=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        DAG,
        UserContainer,
        Workflow,
        models as m,
        script,
    )


    @script(
        sidecars=[
            UserContainer(name="sidecar-name", volume_mounts=[m.VolumeMount(mount_path="/whatever", name="something")])
        ]
    )
    def foo():
        print("hi")


    with Workflow(
        generate_name="sidecar-volume-mount-",
        entrypoint="d",
        volume_claim_templates=[
            m.PersistentVolumeClaim(
                metadata=m.ObjectMeta(name="something"),
                spec=m.PersistentVolumeClaimSpec(
                    access_modes=["ReadWriteOnce"],
                    resources=m.VolumeResourceRequirements(requests={"storage": "64Mi"}),
                ),
            )
        ],
    ) as w:
        with DAG(name="d"):
            foo()
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: sidecar-volume-mount-
    spec:
      entrypoint: d
      templates:
      - name: d
        dag:
          tasks:
          - name: foo
            template: foo
      - name: foo
        sidecars:
        - name: sidecar-name
          volumeMounts:
          - name: something
            mountPath: /whatever
        script:
          image: python:3.10
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print('hi')
          command:
          - python
      volumeClaimTemplates:
      - metadata:
          name: something
        spec:
          accessModes:
          - ReadWriteOnce
          resources:
            requests:
              storage: 64Mi
    ```

