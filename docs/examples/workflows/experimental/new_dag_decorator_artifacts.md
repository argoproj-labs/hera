# New Dag Decorator Artifacts






=== "Hera"

    ```python linenums="1"
    from typing_extensions import Annotated

    from hera.shared import global_config
    from hera.workflows import Artifact, ArtifactLoader, Input, Output, Workflow

    global_config.experimental_features["decorator_syntax"] = True


    w = Workflow(generate_name="my-workflow-")


    class ArtifactOutput(Output):
        an_artifact: Annotated[str, Artifact(name="an-artifact")]


    class ConcatInput(Input):
        word_a: Annotated[str, Artifact(name="word_a", loader=ArtifactLoader.json)]
        word_b: Annotated[str, Artifact(name="word_b", loader=ArtifactLoader.json)]


    @w.script()
    def concat(concat_input: ConcatInput) -> ArtifactOutput:
        return ArtifactOutput(an_artifact=f"{concat_input.word_a} {concat_input.word_b}")


    class WorkerInput(Input):
        artifact_a: Annotated[str, Artifact(name="artifact_a")]
        artifact_b: Annotated[str, Artifact(name="artifact_b")]


    @w.set_entrypoint
    @w.dag()
    def worker(worker_input: WorkerInput) -> ArtifactOutput:
        concat_1 = concat(
            ConcatInput(
                word_a=worker_input.artifact_a,
                word_b=worker_input.artifact_b,
            )
        )

        concat_2 = concat(
            ConcatInput(
                word_a=concat_1.an_artifact,
                word_b=concat_1.an_artifact,
            ),
            name="concat-2-custom-name",
        )

        return ArtifactOutput(an_artifact=concat_2.an_artifact)
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: my-workflow-
    spec:
      entrypoint: worker
      templates:
      - inputs:
          artifacts:
          - name: word_a
            path: /tmp/hera-inputs/artifacts/word_a
          - name: word_b
            path: /tmp/hera-inputs/artifacts/word_b
        name: concat
        outputs:
          artifacts:
          - name: an-artifact
            path: /tmp/hera-outputs/artifacts/an-artifact
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.new_dag_decorator_artifacts:concat
          command:
          - python
          env:
          - name: hera__outputs_directory
            value: /tmp/hera-outputs
          - name: hera__script_pydantic_io
            value: ''
          image: python:3.9
          source: '{{inputs.parameters}}'
      - dag:
          tasks:
          - arguments:
              artifacts:
              - from: '{{inputs.artifacts.artifact_a}}'
                name: word_a
              - from: '{{inputs.artifacts.artifact_b}}'
                name: word_b
            name: concat-1
            template: concat
          - arguments:
              artifacts:
              - from: '{{tasks.concat-1.outputs.artifacts.an-artifact}}'
                name: word_a
              - from: '{{tasks.concat-1.outputs.artifacts.an-artifact}}'
                name: word_b
            depends: concat-1
            name: concat-2-custom-name
            template: concat
        inputs:
          artifacts:
          - name: artifact_a
          - name: artifact_b
        name: worker
        outputs:
          artifacts:
          - from: '{{tasks.concat-2-custom-name.outputs.artifacts.an-artifact}}'
            name: an-artifact
    ```

