# Script Annotations Artifact Loaders






=== "Hera"

    ```python linenums="1"
    from typing import Dict
    import json
    from pathlib import Path

    try:
        from typing import Annotated  # type: ignore
    except ImportError:
        from typing_extensions import Annotated  # type: ignore

    from hera.shared import global_config
    from hera.workflows import Artifact, Parameter, Workflow, script, Steps, ArtifactLoader

    global_config.experimental_features["script_annotations"] = True
    global_config.experimental_features["script_runner"] = True


    @script(constructor="runner")
    def output_dict_artifact(
        a_number: Annotated[int, Parameter(name="a_number")],
    ) -> Annotated[Dict[str, int], Artifact(name="a_dict")]:
        return {"your-value": a_number}


    @script(constructor="runner")
    def artifact_loaders(
        a_file_as_path: Annotated[Path, Artifact(name="my-artifact-path", loader=None)],
        a_file_as_str: Annotated[str, Artifact(name="my-artifact-as-str", loader=ArtifactLoader.file)],
        a_file_as_json: Annotated[Dict, Artifact(name="my-artifact-as-json", loader=ArtifactLoader.json)],
    ):
        assert a_file_as_path.read_text() == a_file_as_str
        assert json.loads(a_file_as_str) == a_file_as_json
        print(a_file_as_path)
        print(a_file_as_str)
        print(a_file_as_json)


    with Workflow(generate_name="test-input-annotations-", entrypoint="my-steps") as w:
        with Steps(name="my-steps") as s:
            out = output_dict_artifact(arguments={"a_number": 3})
            artifact_loaders(
                arguments=[
                    out.get_artifact("a_dict").with_name("my-artifact-path"),
                    out.get_artifact("a_dict").with_name("my-artifact-as-str"),
                    out.get_artifact("a_dict").with_name("my-artifact-as-json"),
                ]
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: test-input-annotations-
    spec:
      entrypoint: my-steps
      templates:
      - name: my-steps
        steps:
        - - arguments:
              parameters:
              - name: a_number
                value: '3'
            name: output-dict-artifact
            template: output-dict-artifact
        - - arguments:
              artifacts:
              - from: '{{steps.output-dict-artifact.outputs.artifacts.a_dict}}'
                name: my-artifact-path
              - from: '{{steps.output-dict-artifact.outputs.artifacts.a_dict}}'
                name: my-artifact-as-str
              - from: '{{steps.output-dict-artifact.outputs.artifacts.a_dict}}'
                name: my-artifact-as-json
            name: artifact-loaders
            template: artifact-loaders
      - inputs:
          parameters:
          - name: a_number
        name: output-dict-artifact
        outputs:
          artifacts:
          - name: a_dict
            path: /tmp/hera/outputs/artifacts/a_dict
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.script_annotations_artifact_loaders:output_dict_artifact
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
          - name: my-artifact-path
            path: /tmp/hera/inputs/artifacts/my-artifact-path
          - name: my-artifact-as-str
            path: /tmp/hera/inputs/artifacts/my-artifact-as-str
          - name: my-artifact-as-json
            path: /tmp/hera/inputs/artifacts/my-artifact-as-json
        name: artifact-loaders
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.script_annotations_artifact_loaders:artifact_loaders
          command:
          - python
          env:
          - name: hera__script_annotations
            value: ''
          image: python:3.8
          source: '{{inputs.parameters}}'
    ```

