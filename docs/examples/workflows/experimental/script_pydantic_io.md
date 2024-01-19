# Script Pydantic Io






=== "Hera"

    ```python linenums="1"
    try:
        from pydantic.v1 import BaseModel
    except ImportError:
        from pydantic import BaseModel

    from hera.shared import global_config
    from hera.workflows import Artifact, ArtifactLoader, Parameter, Workflow, script
    from hera.workflows.io.v1 import RunnerInput, RunnerOutput

    try:
        from typing import Annotated  # type: ignore
    except ImportError:
        from typing_extensions import Annotated  # type: ignore

    global_config.experimental_features["script_annotations"] = True
    global_config.experimental_features["script_pydantic_io"] = True


    class MyObject(BaseModel):
        a_dict: dict = {}
        a_str: str = "a default string"


    class MyInput(RunnerInput):
        param_int: Annotated[int, Parameter(name="param-input")] = 42
        an_object: Annotated[MyObject, Parameter(name="obj-input")] = MyObject(
            a_dict={"my-key": "a-value"}, a_str="hello world!"
        )
        artifact_int: Annotated[int, Artifact(name="artifact-input", loader=ArtifactLoader.json)]


    class MyOutput(RunnerOutput):
        param_int: Annotated[int, Parameter(name="param-output")]
        artifact_int: Annotated[int, Artifact(name="artifact-output")]


    @script(constructor="runner")
    def pydantic_io(
        my_input: MyInput,
    ) -> MyOutput:
        return MyOutput(exit_code=1, result="Test!", param_int=42, artifact_int=my_input.param_int)


    with Workflow(generate_name="pydantic-io-") as w:
        pydantic_io()
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: pydantic-io-
    spec:
      templates:
      - inputs:
          artifacts:
          - name: artifact-input
            path: /tmp/hera-inputs/artifacts/artifact-input
          parameters:
          - default: '42'
            name: param-input
          - default: '{"a_dict": {"my-key": "a-value"}, "a_str": "hello world!"}'
            name: obj-input
        name: pydantic-io
        outputs:
          artifacts:
          - name: artifact-output
            path: /tmp/hera-outputs/artifacts/artifact-output
          parameters:
          - name: param-output
            valueFrom:
              path: /tmp/hera-outputs/parameters/param-output
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.script_pydantic_io:pydantic_io
          command:
          - python
          env:
          - name: hera__script_annotations
            value: ''
          - name: hera__outputs_directory
            value: /tmp/hera-outputs
          - name: hera__script_pydantic_io
            value: ''
          image: python:3.8
          source: '{{inputs.parameters}}'
    ```

