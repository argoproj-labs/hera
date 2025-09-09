# New Data Decorator



This example shows the use of the data decorator and special Input/Output classes.


=== "Hera"

    ```python linenums="1"
    from typing_extensions import Annotated

    from hera.expr import g, it
    from hera.shared import global_config
    from hera.workflows import (
        Artifact,
        Input,
        Output,
        S3Artifact,
        Workflow,
    )

    global_config.experimental_features["decorator_syntax"] = True


    # We start by defining our Workflow
    w = Workflow(generate_name="data-workflow-")


    # This defines the template's inputs
    class MyInput(Input):
        bucket_name: str = "my-bucket"


    class MyOutput(Output):
        file: Annotated[str, Artifact(path="/file")]


    # We then use the decorators of the `Workflow` object
    # to set the entrypoint and create a Data template
    @w.set_entrypoint
    @w.data_template(
        source=S3Artifact(name="test-bucket", bucket=f"{g.inputs.parameters.bucket_name:$}"),
        transformations=[g.data.filter(it.ends_with("main.log"))],  # type: ignore
    )
    def basic_hello_world(my_input: MyInput) -> MyOutput: ...
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: data-workflow-
    spec:
      entrypoint: basic-hello-world
      templates:
      - name: basic-hello-world
        data:
          transformation:
          - expression: filter(data, {# endsWith 'main.log'})
          source:
            artifactPaths:
              name: test-bucket
              s3:
                bucket: '{{inputs.parameters.bucket_name}}'
        inputs:
          parameters:
          - name: bucket_name
            default: my-bucket
        outputs:
          artifacts:
          - name: file
            path: /file
    ```

