# Artifact Loaders






=== "Hera"

    ```python linenums="1"
    import json
    from pathlib import Path
    from typing import Annotated, Dict

    from hera.workflows import Artifact, ArtifactLoader, Parameter, Steps, Workflow, script


    @script(constructor="runner")
    def output_dict_artifact(
        a_number: Annotated[int, Parameter(name="a_number")],
    ) -> Annotated[Dict[str, int], Artifact(name="an-artifact")]:
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


    with Workflow(generate_name="artifact-loaders-", entrypoint="my-steps") as w:
        with Steps(name="my-steps") as s:
            out = output_dict_artifact(arguments={"a_number": 3})
            artifact_loaders(
                arguments={
                    "my-artifact-path": out.get_artifact("an-artifact"),
                    "my-artifact-as-str": out.get_artifact("an-artifact"),
                    "my-artifact-as-json": out.get_artifact("an-artifact"),
                }
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: artifact-loaders-
    spec:
      entrypoint: my-steps
      templates:
      - name: my-steps
        steps:
        - - name: output-dict-artifact
            template: output-dict-artifact
            arguments:
              parameters:
              - name: a_number
                value: '3'
        - - name: artifact-loaders
            template: artifact-loaders
            arguments:
              artifacts:
              - name: my-artifact-path
                from: '{{steps.output-dict-artifact.outputs.artifacts.an-artifact}}'
              - name: my-artifact-as-str
                from: '{{steps.output-dict-artifact.outputs.artifacts.an-artifact}}'
              - name: my-artifact-as-json
                from: '{{steps.output-dict-artifact.outputs.artifacts.an-artifact}}'
      - name: output-dict-artifact
        inputs:
          parameters:
          - name: a_number
        outputs:
          artifacts:
          - name: an-artifact
            path: /tmp/hera-outputs/artifacts/an-artifact
        script:
          image: python:3.9
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.artifacts.artifact_loaders:output_dict_artifact
          command:
          - python
          env:
          - name: hera__outputs_directory
            value: /tmp/hera-outputs
      - name: artifact-loaders
        inputs:
          artifacts:
          - name: my-artifact-path
            path: /tmp/hera-inputs/artifacts/my-artifact-path
          - name: my-artifact-as-str
            path: /tmp/hera-inputs/artifacts/my-artifact-as-str
          - name: my-artifact-as-json
            path: /tmp/hera-inputs/artifacts/my-artifact-as-json
        script:
          image: python:3.9
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.artifacts.artifact_loaders:artifact_loaders
          command:
          - python
    ```

