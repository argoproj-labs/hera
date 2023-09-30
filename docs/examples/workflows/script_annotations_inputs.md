# Script Annotations Inputs






=== "Hera"

    ```python linenums="1"
    try:
        from typing import Annotated  # type: ignore
    except ImportError:
        from typing_extensions import Annotated  # type: ignore

    from hera.shared import global_config
    from hera.workflows import Artifact, Parameter, Workflow, script, Steps, ArtifactLoader

    global_config.experimental_features["script_annotations"] = True
    global_config.experimental_features["script_runner"] = True


    @script(constructor="runner")
    def echo_all(
        an_int: Annotated[int, Parameter(description="an_int parameter", default=1)],
        a_bool: Annotated[bool, Parameter(description="a_bool parameter", default=True)],
        a_string: Annotated[str, Parameter(description="a_string parameter", default="a")],
        # note that this artifact is loaded from tmp/file into an_artifact as a string
        an_artifact: Annotated[str, Artifact(name="my-artifact", path="/tmp/file", loader=ArtifactLoader.file)],
    ):
        print(an_int)
        print(a_bool)
        print(a_string)
        print(an_artifact)


    with Workflow(generate_name="test-input-annotations-", entrypoint="my-steps") as w:
        with Steps(name="my-steps") as s:
            echo_all(
                arguments=[
                    Parameter(name="an_int", value=1),
                    Parameter(name="a_bool", value=True),
                    Parameter(name="a_string", value="a"),
                    Artifact(name="my-artifact", from_="somewhere"),
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
        - - arguments:
              artifacts:
              - from: somewhere
                name: my-artifact
              parameters:
              - name: an_int
                value: '1'
              - name: a_bool
                value: 'true'
              - name: a_string
                value: a
            name: echo-all
            template: echo-all
      - inputs:
          artifacts:
          - name: my-artifact
            path: /tmp/file
          parameters:
          - default: '1'
            description: an_int parameter
            name: an_int
          - default: 'true'
            description: a_bool parameter
            name: a_bool
          - default: a
            description: a_string parameter
            name: a_string
        name: echo-all
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.script_annotations_inputs:echo_all
          command:
          - python
          env:
          - name: hera__script_annotations
            value: ''
          image: python:3.8
          source: '{{inputs.parameters}}'
    ```

