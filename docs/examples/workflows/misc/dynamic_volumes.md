# Dynamic Volumes






=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Volume, Workflow, script


    @script(volumes=Volume(name="v", size="1Gi", mount_path="/mnt/vol"))
    def foo():
        import subprocess

        print(subprocess.run("cd && /mnt && df -h", shell=True, capture_output=True).stdout.decode())


    with Workflow(generate_name="dynamic-volumes-", entrypoint="d") as w:
        with DAG(name="d"):
            foo()
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dynamic-volumes-
    spec:
      entrypoint: d
      templates:
      - name: d
        dag:
          tasks:
          - name: foo
            template: foo
      - name: foo
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import subprocess
            print(subprocess.run('cd && /mnt && df -h', shell=True, capture_output=True).stdout.decode())
          command:
          - python
          volumeMounts:
          - name: v
            mountPath: /mnt/vol
      volumeClaimTemplates:
      - metadata:
          name: v
        spec:
          accessModes:
          - ReadWriteOnce
          resources:
            requests:
              storage: 1Gi
    ```

