# Pydantic Io In Dag Context






=== "Hera"

    ```python linenums="1"
    import sys
    from typing import List

    if sys.version_info >= (3, 9):
        from typing import Annotated
    else:
        from typing_extensions import Annotated


    from hera.shared import global_config
    from hera.workflows import DAG, Parameter, WorkflowTemplate, script
    from hera.workflows.io.v1 import Input, Output

    global_config.experimental_features["decorator_syntax"] = True


    class CutInput(Input):
        cut_after: Annotated[int, Parameter(name="cut-after")]
        strings: List[str]


    class CutOutput(Output):
        first_strings: Annotated[List[str], Parameter(name="first-strings")]
        remainder: List[str]


    class JoinInput(Input):
        strings: List[str]
        joiner: str


    class JoinOutput(Output):
        joined_string: Annotated[str, Parameter(name="joined-string")]


    @script(constructor="runner")
    def cut(input: CutInput) -> CutOutput:
        return CutOutput(
            first_strings=input.strings[: input.cut_after],
            remainder=input.strings[input.cut_after :],
            exit_code=1 if len(input.strings) <= input.cut_after else 0,
        )


    @script(constructor="runner")
    def join(input: JoinInput) -> JoinOutput:
        return JoinOutput(joined_string=input.joiner.join(input.strings))


    with WorkflowTemplate(generate_name="pydantic-io-in-steps-context-v1-", entrypoint="d") as w:
        with DAG(name="d"):
            cut_result = cut(CutInput(strings=["hello", "world", "it's", "hera"], cut_after=1))
            join(JoinInput(strings=cut_result.first_strings, joiner=" "))
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: WorkflowTemplate
    metadata:
      generateName: pydantic-io-in-steps-context-v1-
    spec:
      entrypoint: d
      templates:
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: cut-after
                value: '1'
              - name: strings
                value: '["hello", "world", "it''s", "hera"]'
            name: cut
            template: cut
          - arguments:
              parameters:
              - name: strings
                value: '{{tasks.cut.outputs.parameters.first-strings}}'
              - name: joiner
                value: ' '
            depends: cut
            name: join
            template: join
        name: d
      - inputs:
          parameters:
          - name: cut-after
          - name: strings
        name: cut
        outputs:
          parameters:
          - name: first-strings
            valueFrom:
              path: /tmp/hera-outputs/parameters/first-strings
          - name: remainder
            valueFrom:
              path: /tmp/hera-outputs/parameters/remainder
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.pydantic_io_in_dag_context:cut
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
      - inputs:
          parameters:
          - name: strings
          - name: joiner
        name: join
        outputs:
          parameters:
          - name: joined-string
            valueFrom:
              path: /tmp/hera-outputs/parameters/joined-string
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.pydantic_io_in_dag_context:join
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

