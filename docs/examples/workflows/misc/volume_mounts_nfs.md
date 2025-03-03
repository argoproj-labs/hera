# Volume Mounts Nfs






=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        DAG,
        NFSVolume,
        Parameter,
        Workflow,
        models as m,
        script,
    )


    @script(
        inputs=Parameter(name="vol"),
        volume_mounts=[m.VolumeMount(name="{{inputs.parameters.vol}}", mount_path="/mnt/nfs")],
    )
    def foo():
        import os
        import subprocess

        print(os.listdir("/mnt"))
        print(subprocess.run("cd /mnt && df -h", shell=True, capture_output=True).stdout.decode())


    with Workflow(
        generate_name="volumes-",
        volumes=[
            NFSVolume(
                name="nfs-volume",
                server="your.nfs.server",
                mount_path="/mnt/nfs",
                path="/share/nfs",
            )
        ],
        entrypoint="d",
    ) as w:
        with DAG(name="d"):
            foo(name="v1", arguments=Parameter(name="vol", value="nfs-volume"))
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: volumes-
    spec:
      entrypoint: d
      templates:
      - name: d
        dag:
          tasks:
          - name: v1
            template: foo
            arguments:
              parameters:
              - name: vol
                value: nfs-volume
      - name: foo
        inputs:
          parameters:
          - name: vol
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import os
            import subprocess
            print(os.listdir('/mnt'))
            print(subprocess.run('cd /mnt && df -h', shell=True, capture_output=True).stdout.decode())
          command:
          - python
          volumeMounts:
          - name: '{{inputs.parameters.vol}}'
            mountPath: /mnt/nfs
      volumes:
      - name: nfs-volume
        nfs:
          path: /share/nfs
          server: your.nfs.server
    ```

