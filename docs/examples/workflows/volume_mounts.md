# Volume Mounts






=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        DAG,
        Parameter,
        Volume,
        Workflow,
        models as m,
        script,
    )


    @script(
        inputs=Parameter(name="vol"),
        volume_mounts=[m.VolumeMount(name="{{inputs.parameters.vol}}", mount_path="/mnt/vol")],
    )
    def foo():
        import os
        import subprocess

        print(os.listdir("/mnt"))
        print(subprocess.run("cd /mnt && df -h", shell=True, capture_output=True).stdout.decode())


    with Workflow(
        generate_name="volumes-",
        entrypoint="d",
        volumes=[
            Volume(name="v1", size="1Gi"),
            Volume(name="v2", size="3Gi"),
            Volume(name="v3", size="5Gi"),
        ],
    ) as w:
        with DAG(name="d"):
            foo(name="v1", arguments=Parameter(name="vol", value="v1"))
            foo(name="v2", arguments=Parameter(name="vol", value="v2"))
            foo(name="v3", arguments=Parameter(name="vol", value="v3"))
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
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: vol
                value: v1
            name: v1
            template: foo
          - arguments:
              parameters:
              - name: vol
                value: v2
            name: v2
            template: foo
          - arguments:
              parameters:
              - name: vol
                value: v3
            name: v3
            template: foo
        name: d
      - inputs:
          parameters:
          - name: vol
        name: foo
        script:
          command:
          - python
          image: python:3.8
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            import os

            import subprocess

            print(os.listdir(''/mnt''))

            print(subprocess.run(''cd /mnt && df -h'', shell=True, capture_output=True).stdout.decode())'
          volumeMounts:
          - mountPath: /mnt/vol
            name: '{{inputs.parameters.vol}}'
      volumeClaimTemplates:
      - metadata:
          name: v1
        spec:
          accessModes:
          - ReadWriteOnce
          resources:
            requests:
              storage: 1Gi
      - metadata:
          name: v2
        spec:
          accessModes:
          - ReadWriteOnce
          resources:
            requests:
              storage: 3Gi
      - metadata:
          name: v3
        spec:
          accessModes:
          - ReadWriteOnce
          resources:
            requests:
              storage: 5Gi
    ```

