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


    with Workflow(generate_name="sidecar-volume-mount-", entrypoint="d") as w:
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
      - dag:
          tasks:
          - name: foo
            template: foo
        name: d
      - name: foo
        script:
          command:
          - python
          image: python:3.8
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            print(''hi'')'
        sidecars:
        - name: sidecar-name
          volumeMounts:
          - mountPath: /whatever
            name: something
    ```

