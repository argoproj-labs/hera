# Script Annotations Inputs






=== "Hera"

    ```python linenums="1"
    from typing import Annotated, Dict

    from hera.workflows import Artifact, ArtifactLoader, Parameter, Steps, Workflow, script


    @script(constructor="runner")
    def output_dict_artifact(
        a_number: Annotated[int, Parameter(name="a_number")],
    ) -> Annotated[Dict[str, int], Artifact(name="a_dict")]:
        return {"your-value": a_number}


    @script(constructor="runner")
    def echo_all(
        # note that this artifact is loaded from /tmp/file into an_artifact as a string
        an_artifact: Annotated[str, Artifact(name="my-artifact", path="/tmp/file", loader=ArtifactLoader.file)],
        # note that this automatically uses the path /tmp/hera/inputs/artifacts/my-artifact-no-path
        an_artifact_no_path: Annotated[str, Artifact(name="my-artifact-no-path", loader=ArtifactLoader.file)],
        an_int: Annotated[int, Parameter(description="an_int parameter")] = 1,
        a_bool: Annotated[bool, Parameter(description="a_bool parameter")] = True,
        a_string: Annotated[str, Parameter(description="a_string parameter")] = "a",
    ):
        print(an_int)
        print(a_bool)
        print(a_string)
        print(an_artifact)
        print(an_artifact_no_path)


    with Workflow(generate_name="test-input-annotations-", entrypoint="my-steps") as w:
        with Steps(name="my-steps") as s:
            out = output_dict_artifact(arguments={"a_number": 3})
            echo_all(
                arguments=[
                    Parameter(name="an_int", value=1),
                    Parameter(name="a_bool", value=True),
                    Parameter(name="a_string", value="a"),
                    out.get_artifact("a_dict").with_name("my-artifact"),
                    out.get_artifact("a_dict").with_name("my-artifact-no-path"),
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
        - - name: output-dict-artifact
            template: output-dict-artifact
            arguments:
              parameters:
              - name: a_number
                value: '3'
        - - name: echo-all
            template: echo-all
            arguments:
              artifacts:
              - name: my-artifact
                from: '{{steps.output-dict-artifact.outputs.artifacts.a_dict}}'
              - name: my-artifact-no-path
                from: '{{steps.output-dict-artifact.outputs.artifacts.a_dict}}'
              parameters:
              - name: an_int
                value: '1'
              - name: a_bool
                value: 'true'
              - name: a_string
                value: a
      - name: output-dict-artifact
        inputs:
          parameters:
          - name: a_number
        outputs:
          artifacts:
          - name: a_dict
            path: /tmp/hera-outputs/artifacts/a_dict
        script:
          image: python:3.9
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.scripts.script_annotations_inputs:output_dict_artifact
          command:
          - python
          env:
          - name: hera__outputs_directory
            value: /tmp/hera-outputs
      - name: echo-all
        inputs:
          artifacts:
          - name: my-artifact
            path: /tmp/file
          - name: my-artifact-no-path
            path: /tmp/hera-inputs/artifacts/my-artifact-no-path
          parameters:
          - name: an_int
            default: '1'
            description: an_int parameter
          - name: a_bool
            default: 'true'
            description: a_bool parameter
          - name: a_string
            default: a
            description: a_string parameter
        script:
          image: python:3.9
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.scripts.script_annotations_inputs:echo_all
          command:
          - python
    ```

