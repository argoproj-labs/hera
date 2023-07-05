# Init Container

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/init-container.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Container,
        EmptyDirVolume,
        UserContainer,
        Workflow,
        models as m,
    )

    with Workflow(
        generate_name="init-container-", entrypoint="init-container-example", volumes=EmptyDirVolume(name="foo")
    ) as w:
        init_container_example = Container(
            name="init-container-example",
            image="alpine:latest",
            command=["echo", "bye"],
            volume_mounts=[m.VolumeMount(name="foo", mount_path="/foo")],
            init_containers=[
                UserContainer(
                    name="hello",
                    image="alpine:latest",
                    command=["echo", "hello"],
                    mirror_volume_mounts=True,
                ),
            ],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: init-container-
    spec:
      entrypoint: init-container-example
      templates:
      - container:
          command:
          - echo
          - bye
          image: alpine:latest
          volumeMounts:
          - mountPath: /foo
            name: foo
        initContainers:
        - command:
          - echo
          - hello
          image: alpine:latest
          mirrorVolumeMounts: true
          name: hello
        name: init-container-example
      volumes:
      - emptyDir: {}
        name: foo
    ```

