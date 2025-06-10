# Basic Artifacts



Compare this example to [Basic Artifacts](../artifacts/basic_artifacts.md) to see how the Hera runner simplifies your Artifact code.


=== "Hera"

    ```python linenums="1"
    from typing import Annotated

    from hera.workflows import (
        Artifact,
        NoneArchiveStrategy,
        Steps,
        Workflow,
        script,
    )
    from hera.workflows.artifact import ArtifactLoader


    @script()
    def writer() -> Annotated[str, Artifact(name="out-art", archive=NoneArchiveStrategy())]:
        return "Hello, world!"


    @script()
    def consumer(
        in_art: Annotated[
            str,
            Artifact(loader=ArtifactLoader.json),
        ],
    ):
        print(in_art)  # prints `Hello, world!` to `stdout`


    with Workflow(generate_name="artifact-", entrypoint="steps") as w:
        with Steps(name="steps"):
            w_ = writer()
            c = consumer(arguments={"in_art": w_.get_artifact("out-art")})
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: artifact-
    spec:
      entrypoint: steps
      templates:
      - name: steps
        steps:
        - - name: writer
            template: writer
        - - name: consumer
            template: consumer
            arguments:
              artifacts:
              - name: in_art
                from: '{{steps.writer.outputs.artifacts.out-art}}'
      - name: writer
        outputs:
          artifacts:
          - name: out-art
            archive:
              none: {}
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            return 'Hello, world!'
          command:
          - python
      - name: consumer
        inputs:
          artifacts:
          - name: in_art
            path: /tmp/hera-inputs/artifacts/in_art
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print(in_art)
          command:
          - python
    ```

