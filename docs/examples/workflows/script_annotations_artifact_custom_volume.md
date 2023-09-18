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
        Parameter,
        RunnerScriptConstructor,
        Steps,
        Workflow,
        models as m,
        script,
    )

    global_config.experimental_features["script_annotations"] = True
    global_config.experimental_features["script_runner"] = True

    vol = Volume(name="my-vol", size="1Gi")


    @script(
        constructor=RunnerScriptConstructor(outputs_directory="/mnt/here", use_volume_for_outputs=vol.name),
        volume_mounts=[m.VolumeMount(name="my-vol", mount_path="/mnt/here")],
    )
    def output_artifact(
        a_number: Annotated[int, Parameter(name="a_number")],
    ) -> Annotated[int, Artifact(name="successor_out")]:
        return a_number + 1


    @script(
        constructor=RunnerScriptConstructor(),
        volume_mounts=[m.VolumeMount(name="my-vol", mount_path="/mnt/here")],
    )
    def use_artifact(successor_in: Annotated[int, Artifact(name="successor_in", loader=ArtifactLoader.json)]):
        print(successor_in)


    with Workflow(
        generate_name="test-output-annotations-",
        entrypoint="my-steps",
        volumes=[vol],
    ) as w:
        with Steps(name="my-steps") as s:
            out = output_artifact(arguments={"a_number": 3})
            use_artifact(arguments=[out.get_artifact("successor_out").as_name("successor_in")])
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
            name: output-artifact
            template: output-artifact
        - - arguments:
              artifacts:
              - from: '{{steps.output-artifact.outputs.artifacts.successor_out}}'
                name: successor_in
            name: use-artifact
            template: use-artifact
      - inputs:
          parameters:
          - name: a_number
        name: output-artifact
        outputs:
          artifacts:
          - name: successor_out
            path: /mnt/here/artifacts/successor_out
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.script_annotations_artifact_custom_volume:output_artifact
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

