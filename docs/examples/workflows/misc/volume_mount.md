# Volume Mount



This example showcases how to create a volume at a workflow level and use it in a container via a mount.


=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, SecretVolume, Steps, Volume, Workflow
    from hera.workflows.models import VolumeMount

    with Workflow(
        generate_name="volume-mount-",
        volumes=[SecretVolume(name="service-account-credential", secret_name="service-account-credential")],
        entrypoint="test",
    ) as w:
        v_tmp_pod = Volume(
            name="tmp-pod",
            size="100Mi",
            mount_path="/tmp/pod",
        )
        init_container_example = Container(
            name="git-sync",
            volume_mounts=[VolumeMount(name="service-account-credential", mount_path="/secrets")],
            volumes=[v_tmp_pod],
        )
        with Steps(name="test") as s:
            init_container_example()
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: volume-mount-
    spec:
      entrypoint: test
      templates:
      - name: git-sync
        container:
          image: python:3.10
          volumeMounts:
          - name: service-account-credential
            mountPath: /secrets
          - name: tmp-pod
            mountPath: /tmp/pod
      - name: test
        steps:
        - - name: git-sync
            template: git-sync
      volumeClaimTemplates:
      - metadata:
          name: tmp-pod
        spec:
          accessModes:
          - ReadWriteOnce
          resources:
            requests:
              storage: 100Mi
      volumes:
      - name: service-account-credential
        secret:
          secretName: service-account-credential
    ```

