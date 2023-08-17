# Script Annotations Outputs






=== "Hera"

    ```python linenums="1"
    import os

    try:
        from typing import Annotated  # type: ignore
    except ImportError:
        from typing_extensions import Annotated  # type: ignore

    from pathlib import Path

    from typing import Tuple

    from hera.shared import global_config
    from hera.workflows import Artifact, Parameter, Workflow, script, Steps, RunnerScriptConstructor

    global_config.experimental_features["script_annotations"] = True
    global_config.experimental_features["script_runner"] = True

    global_config.set_class_defaults(RunnerScriptConstructor, outputs_directory="user/chosen/outputs")


    @script(constructor="runner")
    def script_param_artifact_in_function_signature_and_return_type(
        a_number: Annotated[int, Parameter(name="a_number")],
        successor: Annotated[Path, Parameter(name="successor", output=True)],
        successor2: Annotated[Path, Artifact(name="successor2", output=True)],
    ) -> Tuple[
        Annotated[int, Parameter(name="successor3", output=True)], Annotated[int, Artifact(name="successor4", output=True)]
    ]:
        successor.write_text(a_number + 1)
        successor2.write_text(a_number + 2)
        return a_number + 3, a_number + 4


    with Workflow(generate_name="test-output-annotations-", entrypoint="my_steps") as w:
        with Steps(name="my_steps") as s:
            script_param_artifact_in_function_signature_and_return_type(arguments={"a_number": 3})
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: test-output-annotations-
    spec:
      entrypoint: my_steps
      templates:
      - name: my_steps
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
          - name: successor4
          parameters:
          - name: successor
          - name: successor3
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
            value: user/chosen/outputs
          image: python:3.8
          source: '{{inputs.parameters}}'
          volumeMounts:
          - mountPath: user/chosen/outputs
            name: hera__outputs_directory
        volumes:
        - emptyDir: {}
          name: hera__outputs_directory
    ```

