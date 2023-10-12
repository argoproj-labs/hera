# Script Annotations Artifact Custom Volume



This example will reuse the outputs volume across script steps.


=== "Hera"

    ```python linenums="1"
    from hera.workflows.artifact import ArtifactLoader
    from hera.workflows.volume import Volume

    try:
        from typing import Annotated  # type: ignore
    except ImportError:
        from typing_extensions import Annotated  # type: ignore


    from hera.shared import global_config
    from hera.workflows import (
        Artifact,
        EmptyDirVolume,
        Parameter,
        RunnerScriptConstructor,
        Steps,
        Workflow,
        models as m,
        script,
    )

    global_config.experimental_features["script_annotations"] = True
    global_config.experimental_features["script_runner"] = True


    @script(
        constructor=RunnerScriptConstructor(
            outputs_directory="/mnt/empty/dir",
            volume_for_outputs=EmptyDirVolume(name="my-empty-dir"),
        ),
    )
    def output_artifact_empty_dir(
        a_number: Annotated[int, Parameter(name="a_number")],
    ) -> Annotated[int, Artifact(name="successor_out")]:
        return a_number + 1


    @script(
        constructor=RunnerScriptConstructor(),  # Has no outputs
    )
    def use_artifact(
        successor_in: Annotated[
            int,
            Artifact(name="successor_in", loader=ArtifactLoader.json),
        ]
    ):
        print(successor_in)


    @script(
        constructor=RunnerScriptConstructor(outputs_directory="/mnt/here"),
        volume_mounts=[
            m.VolumeMount(name="my-vol", mount_path="/mnt/here")
        ],  # Mounting volume created outside of this script
    )
    def output_artifact_existing_vol(
        a_number: Annotated[int, Parameter(name="a_number")],
    ) -> Annotated[int, Artifact(name="successor_out")]:
        return a_number + 1


    @script(
        constructor=RunnerScriptConstructor(),  # no outputs
        volume_mounts=[
            m.VolumeMount(name="my-vol", mount_path="/mnt/here")
        ],  # Mounting volume created outside of this script
    )
    def use_artifact_existing_vol(
        successor_in: Annotated[
            int, Artifact(name="successor_in", path="/mnt/here/artifacts/successor_out", loader=ArtifactLoader.json)
        ],
    ):
        print(successor_in)


    with Workflow(
        generate_name="test-output-annotations-",
        entrypoint="my-steps",
        volumes=[Volume(name="my-vol", size="1Gi")],
    ) as w:
        with Steps(name="my-steps") as s:
            out_to_empty_dir = output_artifact_empty_dir(arguments={"a_number": 3})
            use_artifact(arguments=[out_to_empty_dir.get_artifact("successor_out").with_name("successor_in")])

            out_to_my_vol = output_artifact_existing_vol(arguments={"a_number": 3})
            use_artifact_existing_vol()
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: test-output-annotations-
    spec:
      entrypoint: my-steps
      templates:
      - name: my-steps
        steps:
        - - arguments:
              parameters:
              - name: a_number
                value: '3'
            name: output-artifact-empty-dir
            template: output-artifact-empty-dir
        - - arguments:
              artifacts:
              - from: '{{steps.output-artifact-empty-dir.outputs.artifacts.successor_out}}'
                name: successor_in
            name: use-artifact
            template: use-artifact
        - - arguments:
              parameters:
              - name: a_number
                value: '3'
            name: output-artifact-existing-vol
            template: output-artifact-existing-vol
        - - name: use-artifact-existing-vol
            template: use-artifact-existing-vol
      - inputs:
          parameters:
          - name: a_number
        name: output-artifact-empty-dir
        outputs:
          artifacts:
          - name: successor_out
            path: /mnt/empty/dir/artifacts/successor_out
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.script_annotations_artifact_custom_volume:output_artifact_empty_dir
          command:
          - python
          env:
          - name: hera__script_annotations
            value: ''
          - name: hera__outputs_directory
            value: /mnt/empty/dir
          image: python:3.8
          source: '{{inputs.parameters}}'
          volumeMounts:
          - mountPath: /mnt/empty/dir
            name: my-empty-dir
        volumes:
        - emptyDir: {}
          name: my-empty-dir
      - inputs:
          artifacts:
          - name: successor_in
            path: /tmp/hera/inputs/artifacts/successor_in
        name: use-artifact
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.script_annotations_artifact_custom_volume:use_artifact
          command:
          - python
          env:
          - name: hera__script_annotations
            value: ''
          image: python:3.8
          source: '{{inputs.parameters}}'
      - inputs:
          parameters:
          - name: a_number
        name: output-artifact-existing-vol
        outputs:
          artifacts:
          - name: successor_out
            path: /mnt/here/artifacts/successor_out
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.script_annotations_artifact_custom_volume:output_artifact_existing_vol
          command:
          - python
          env:
          - name: hera__script_annotations
            value: ''
          - name: hera__outputs_directory
            value: /mnt/here
          image: python:3.8
          source: '{{inputs.parameters}}'
          volumeMounts:
          - mountPath: /mnt/here
            name: my-vol
      - inputs:
          artifacts:
          - name: successor_in
            path: /mnt/here/artifacts/successor_out
        name: use-artifact-existing-vol
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.script_annotations_artifact_custom_volume:use_artifact_existing_vol
          command:
          - python
          env:
          - name: hera__script_annotations
            value: ''
          image: python:3.8
          source: '{{inputs.parameters}}'
          volumeMounts:
          - mountPath: /mnt/here
            name: my-vol
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

