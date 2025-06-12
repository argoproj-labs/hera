# Create Volume For Workflow



This example reuses a volume across scripts.

This avoids the performance loss of upload/download to your artifact storage.
Settings a `Volume` on the `Workflow` automatically creates a `volumeClaimTemplate` for the tasks to use.


=== "Hera"

    ```python linenums="1"
    from typing import Annotated

    from hera.workflows import (
        Artifact,
        NoneArchiveStrategy,
        Parameter,
        RunnerScriptConstructor,
        Steps,
        Workflow,
        models as m,
        script,
    )
    from hera.workflows.artifact import ArtifactLoader
    from hera.workflows.volume import Volume


    @script(
        constructor=RunnerScriptConstructor(outputs_directory="/mnt/here"),
        volume_mounts=[
            m.VolumeMount(name="my-vol", mount_path="/mnt/here")
        ],  # We mount the volume created by the Workflow
    )
    def output_artifact_existing_vol(
        a_number: Annotated[int, Parameter(name="a_number")],
    ) -> Annotated[int, Artifact(name="successor_out", archive=NoneArchiveStrategy())]:
        return a_number + 1


    @script(
        constructor=RunnerScriptConstructor(),
        volume_mounts=[
            m.VolumeMount(name="my-vol", mount_path="/mnt/here")
        ],  # We mount the volume created by the Workflow
    )
    def use_artifact_existing_vol(
        successor_in: Annotated[
            int, Artifact(name="successor_in", path="/mnt/here/artifacts/successor_out", loader=ArtifactLoader.json)
        ],
    ):
        print(successor_in)


    with Workflow(
        generate_name="create-volume-for-workflow-",
        entrypoint="my-steps",
        volumes=[Volume(name="my-vol", size="1Gi")],  # Creates a VolumeClaimTemplate (and thus the Volume itself)
    ) as w:
        with Steps(name="my-steps") as s:
            output_task = output_artifact_existing_vol(arguments={"a_number": 3})
            use_artifact_existing_vol(arguments={"successor_in": output_task.get_artifact("successor_out")})
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: create-volume-for-workflow-
    spec:
      entrypoint: my-steps
      templates:
      - name: my-steps
        steps:
        - - name: output-artifact-existing-vol
            template: output-artifact-existing-vol
            arguments:
              parameters:
              - name: a_number
                value: '3'
        - - name: use-artifact-existing-vol
            template: use-artifact-existing-vol
            arguments:
              artifacts:
              - name: successor_in
                from: '{{steps.output-artifact-existing-vol.outputs.artifacts.successor_out}}'
      - name: output-artifact-existing-vol
        inputs:
          parameters:
          - name: a_number
        outputs:
          artifacts:
          - name: successor_out
            path: /mnt/here/artifacts/successor_out
            archive:
              none: {}
        script:
          image: python:3.9
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.artifacts.create_volume_for_workflow:output_artifact_existing_vol
          command:
          - python
          env:
          - name: hera__outputs_directory
            value: /mnt/here
          volumeMounts:
          - name: my-vol
            mountPath: /mnt/here
      - name: use-artifact-existing-vol
        inputs:
          artifacts:
          - name: successor_in
            path: /mnt/here/artifacts/successor_out
        script:
          image: python:3.9
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.artifacts.create_volume_for_workflow:use_artifact_existing_vol
          command:
          - python
          volumeMounts:
          - name: my-vol
            mountPath: /mnt/here
      volumeClaimTemplates:
      - metadata:
          name: my-vol
        spec:
          accessModes:
          - ReadWriteOnce
          resources:
            requests:
              storage: 1Gi
    ```

