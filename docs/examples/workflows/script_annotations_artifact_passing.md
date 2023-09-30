# Script Annotations Artifact Passing



This example will reuse the outputs volume across script steps.


=== "Hera"

    ```python linenums="1"
    try:
        from typing import Annotated  # type: ignore
    except ImportError:
        from typing_extensions import Annotated  # type: ignore


    from pathlib import Path
    from hera.shared import global_config
    from hera.workflows import (
        Artifact,
        ArtifactLoader,
        Parameter,
        Steps,
        Workflow,
        script,
    )

    global_config.experimental_features["script_annotations"] = True
    global_config.experimental_features["script_runner"] = True


    @script(constructor="runner")
    def output_artifact(
        a_number: Annotated[int, Parameter(name="a_number")],
    ) -> Annotated[int, Artifact(name="successor_out")]:
        return a_number + 1


    @script(constructor="runner")
    def use_artifact(
        successor_in: Annotated[
            int,
            Artifact(name="successor_in", path="/my-path", loader=ArtifactLoader.json),
        ]
    ):
        print(successor_in)
        print(Path("/my-path").read_text())  # if you still need the actual path, it is still mounted where you specify


    with Workflow(
        generate_name="annotations-artifact-passing",
        entrypoint="my-steps",
    ) as w:
        with Steps(name="my-steps") as s:
            out = output_artifact(arguments={"a_number": 3})
            use_artifact(arguments=[out.get_artifact("successor_out").with_name("successor_in")])
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: annotations-artifact-passing
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
            path: /tmp/hera/outputs/artifacts/successor_out
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.script_annotations_artifact_passing:output_artifact
          command:
          - python
          env:
          - name: hera__script_annotations
            value: ''
          - name: hera__outputs_directory
            value: /tmp/hera/outputs
          image: python:3.8
          source: '{{inputs.parameters}}'
      - inputs:
          artifacts:
          - name: successor_in
            path: /my-path
        name: use-artifact
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.script_annotations_artifact_passing:use_artifact
          command:
          - python
          env:
          - name: hera__script_annotations
            value: ''
          image: python:3.8
          source: '{{inputs.parameters}}'
    ```

