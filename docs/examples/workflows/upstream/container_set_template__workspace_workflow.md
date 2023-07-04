# Container Set Template  Workspace Workflow

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/container-set-template/workspace-workflow.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import ContainerNode, ContainerSet, EmptyDirVolume, Parameter, Workflow
    from hera.workflows.models import Artifact, ValueFrom, VolumeMount

    with Workflow(
        generate_name="workspace-",
        entrypoint="main",
    ) as w:
        with ContainerSet(
            name="main",
            volumes=[EmptyDirVolume(name="workspace", mount_path="/workspace")],
            volume_mounts=[VolumeMount(name="workspace", mount_path="/workspace")],
            outputs=[
                Parameter(name="out", value_from=ValueFrom(path="/workspace/out")),
                Artifact(name="out", path="/workspace/out"),
            ],
        ):
            ContainerNode(
                name="a",
                image="argoproj/argosay:v2",
                args=["echo", "hi", "/workspace/out"],
            ),
            ContainerNode(
                name="main",
                image="argoproj/argosay:v2",
            ),
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: workspace-
    spec:
      entrypoint: main
      templates:
      - containerSet:
          containers:
          - args:
            - echo
            - hi
            - /workspace/out
            image: argoproj/argosay:v2
            name: a
          - image: argoproj/argosay:v2
            name: main
          volumeMounts:
          - mountPath: /workspace
            name: workspace
        name: main
        outputs:
          artifacts:
          - name: out
            path: /workspace/out
          parameters:
          - name: out
            valueFrom:
              path: /workspace/out
        volumes:
        - emptyDir: {}
          name: workspace
    ```

