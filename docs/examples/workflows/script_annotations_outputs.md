# Script Annotations Outputs






=== "Hera"

    ```python linenums="1"
    try:
        from typing import Annotated  # type: ignore
    except ImportError:
        from typing_extensions import Annotated  # type: ignore

    from pathlib import Path
    from typing import Tuple

    from hera.shared import global_config
    from hera.workflows import Artifact, Parameter, RunnerScriptConstructor, Steps, Workflow, script

    global_config.experimental_features["script_annotations"] = True

    global_config.set_class_defaults(RunnerScriptConstructor, outputs_directory="/tmp/user/chosen/outputs")


    @script(constructor="runner")
    def script_param_artifact_in_function_signature_and_return_type(
        a_number: Annotated[int, Parameter(name="a_number")],
        successor: Annotated[Path, Parameter(name="successor", output=True)],
        successor2: Annotated[Path, Artifact(name="successor2", output=True)],
    ) -> Tuple[Annotated[int, Parameter(name="successor3")], Annotated[int, Artifact(name="successor4")]]:
        successor.write_text(str(a_number + 1))
        successor2.write_text(str(a_number + 2))
        return a_number + 3, a_number + 4


    with Workflow(generate_name="test-output-annotations-", entrypoint="my-steps") as w:
        with Steps(name="my-steps") as s:
            script_param_artifact_in_function_signature_and_return_type(arguments={"a_number": 3})
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
            name: script-param-artifact-in-function-signature-and-return-type
            template: script-param-artifact-in-function-signature-and-return-type
      - inputs:
          parameters:
          - name: a_number
        name: script-param-artifact-in-function-signature-and-return-type
        outputs:
          artifacts:
          - name: successor2
            path: /tmp/user/chosen/outputs/artifacts/successor2
          - name: successor4
            path: /tmp/user/chosen/outputs/artifacts/successor4
          parameters:
          - name: successor
            valueFrom:
              path: /tmp/user/chosen/outputs/parameters/successor
          - name: successor3
            valueFrom:
              path: /tmp/user/chosen/outputs/parameters/successor3
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.script_annotations_outputs:script_param_artifact_in_function_signature_and_return_type
          command:
          - python
          env:
          - name: hera__script_annotations
            value: ''
          - name: hera__outputs_directory
            value: /tmp/user/chosen/outputs
          image: python:3.8
          source: '{{inputs.parameters}}'
    ```

