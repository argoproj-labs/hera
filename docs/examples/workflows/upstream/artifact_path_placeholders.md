# Artifact Path Placeholders

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/artifact-path-placeholders.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Artifact,
        Container,
        Parameter,
        RawArtifact,
        Workflow,
        models as m,
    )

    with Workflow(
        generate_name="artifact-path-placeholders-",
        entrypoint="head-lines",
        arguments=[Parameter(name="lines-count", value=3), RawArtifact(name="text", data="1\n2\n3\n4\n5\n")],
    ) as w:
        Container(
            name="head-lines",
            image="busybox",
            command=[
                "sh",
                "-c",
                'mkdir -p "$(dirname "{{outputs.artifacts.text.path}}")" '
                '"$(dirname "{{outputs.parameters.actual-lines-count.path}}")" ; '
                'head -n {{inputs.parameters.lines-count}} < "{{inputs.artifacts.text.path}}" '
                '| tee "{{outputs.artifacts.text.path}}" | wc -l > "{{outputs.parameters.actual-lines-count.path}}"',
            ],
            inputs=[
                Parameter(name="lines-count"),
                Artifact(name="text", path="/inputs/text/data"),
            ],
            outputs=[
                Parameter(name="actual-lines-count", value_from=m.ValueFrom(path="/outputs/actual-lines-count/data")),
                Artifact(name="text", path="/outputs/text/data"),
            ],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: artifact-path-placeholders-
    spec:
      entrypoint: head-lines
      templates:
      - name: head-lines
        container:
          image: busybox
          command:
          - sh
          - -c
          - mkdir -p "$(dirname "{{outputs.artifacts.text.path}}")" "$(dirname "{{outputs.parameters.actual-lines-count.path}}")"
            ; head -n {{inputs.parameters.lines-count}} < "{{inputs.artifacts.text.path}}"
            | tee "{{outputs.artifacts.text.path}}" | wc -l > "{{outputs.parameters.actual-lines-count.path}}"
        inputs:
          artifacts:
          - name: text
            path: /inputs/text/data
          parameters:
          - name: lines-count
        outputs:
          artifacts:
          - name: text
            path: /outputs/text/data
          parameters:
          - name: actual-lines-count
            valueFrom:
              path: /outputs/actual-lines-count/data
      arguments:
        artifacts:
        - name: text
          raw:
            data: |
              1
              2
              3
              4
              5
        parameters:
        - name: lines-count
          value: '3'
    ```

