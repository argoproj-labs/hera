# New Dag Decorator Artifacts



This example shows how to pass Artifacts between scripts in a dag, using the new decorators.

The DAG decorator function can easily lift out an output artifact from a task as an output of the
DAG itself by referencing it in an `Output` class.


=== "Hera"

    ```python linenums="1"
    from typing import Annotated

    from hera.shared import global_config
    from hera.workflows import (
        Artifact,
        ArtifactLoader,
        Input,
        NoneArchiveStrategy,
        Output,
        Workflow,
    )

    global_config.experimental_features["decorator_syntax"] = True


    w = Workflow(generate_name="artifact-workflow-")


    class ArtifactOutput(Output):
        an_artifact: Annotated[str, Artifact(name="an-artifact", archive=NoneArchiveStrategy())]


    class ConcatInput(Input):
        word_a: Annotated[str, Artifact(name="word_a", loader=ArtifactLoader.file)]
        word_b: Annotated[str, Artifact(name="word_b", loader=ArtifactLoader.file)]


    @w.script()
    def create_artifact() -> ArtifactOutput:
        return ArtifactOutput(an_artifact="hello world")


    @w.script()
    def concat(concat_input: ConcatInput) -> ArtifactOutput:
        return ArtifactOutput(an_artifact=f"{concat_input.word_a} {concat_input.word_b}")


    class WorkerInput(Input):
        artifact_a: Annotated[str, Artifact(name="artifact_a")]
        artifact_b: Annotated[str, Artifact(name="artifact_b")]


    @w.set_entrypoint
    @w.dag()
    def worker() -> ArtifactOutput:
        create = create_artifact()
        concat_1 = concat(
            ConcatInput(
                word_a=create.an_artifact,
                word_b=create.an_artifact,
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
      generateName: artifact-workflow-
    spec:
      entrypoint: worker
      templates:
      - name: create-artifact
        outputs:
          artifacts:
          - name: an-artifact
            path: /tmp/hera-outputs/artifacts/an-artifact
            archive:
              none: {}
        script:
          image: python:3.10
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.new_dag_decorator_artifacts:create_artifact
          command:
          - python
          env:
          - name: hera__outputs_directory
            value: /tmp/hera-outputs
          - name: hera__script_pydantic_io
            value: ''
      - name: concat
        inputs:
          artifacts:
          - name: word_a
            path: /tmp/hera-inputs/artifacts/word_a
          - name: word_b
            path: /tmp/hera-inputs/artifacts/word_b
        outputs:
          artifacts:
          - name: an-artifact
            path: /tmp/hera-outputs/artifacts/an-artifact
            archive:
              none: {}
        script:
          image: python:3.10
          source: '{{inputs.parameters}}'
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
      - name: worker
        dag:
          tasks:
          - name: create
            template: create-artifact
          - name: concat-1
            depends: create
            template: concat
            arguments:
              artifacts:
              - name: word_a
                from: '{{tasks.create.outputs.artifacts.an-artifact}}'
              - name: word_b
                from: '{{tasks.create.outputs.artifacts.an-artifact}}'
          - name: concat-2-custom-name
            depends: concat-1
            template: concat
            arguments:
              artifacts:
              - name: word_a
                from: '{{tasks.concat-1.outputs.artifacts.an-artifact}}'
              - name: word_b
                from: '{{tasks.concat-1.outputs.artifacts.an-artifact}}'
        outputs:
          artifacts:
          - name: an-artifact
            from: '{{tasks.concat-2-custom-name.outputs.artifacts.an-artifact}}'
            archive:
              none: {}
    ```

