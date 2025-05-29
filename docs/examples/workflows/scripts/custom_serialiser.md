# Custom Serialiser



This example shows how to use the custom serialisation features for Parameters and Artifacts.

`pickle` is used to dump `CustomClass` as a binary blob for an Artifact, whereas for a Parameter, we use the provided
serialisation functions in the class.


=== "Hera"

    ```python linenums="1"
    import pickle
    from typing import Annotated, Tuple

    from hera.workflows import (
        DAG,
        Artifact,
        NoneArchiveStrategy,
        Parameter,
        Task,
        Workflow,
        script,
    )


    class CustomClass:
        """Represents a non-user-defined class (e.g. pandas DataFrame) that does not inherit from BaseModel."""

        def __init__(self, a: str, b: str):
            self.a = a
            self.b = b

        @classmethod
        def from_custom(cls, custom: str) -> "CustomClass":
            split = custom.split()
            return cls(a=split[0], b=" custom " + split[1])

        def to_string(self) -> str:
            return f"{self.a} {self.b}"


    @script(constructor="runner", image="my-image:v1")
    def create_outputs() -> Tuple[
        Annotated[
            CustomClass,
            Artifact(
                name="binary-output",
                dumpb=pickle.dumps,
                archive=NoneArchiveStrategy(),
            ),
        ],
        Annotated[CustomClass, Parameter(name="param-output", dumps=lambda x: x.to_string())],
    ]:
        return CustomClass(a="artifact", b="test"), CustomClass(a="parameter", b="test")


    @script(constructor="runner", image="my-image:v1")
    def consume_outputs(
        a_parameter: Annotated[
            CustomClass,
            Parameter(name="my-parameter", loads=CustomClass.from_custom),
        ],
        an_artifact: Annotated[
            CustomClass,
            Artifact(
                name="binary-artifact",
                loadb=lambda b: pickle.loads(b),
            ),
        ],
    ) -> str:
        print(an_artifact)
        return a_parameter.a + a_parameter.b


    with Workflow(generate_name="param-passing-", entrypoint="d", service_account_name="argo") as w:
        with DAG(name="d"):
            create_task: Task = create_outputs()
            consume_task = consume_outputs(
                arguments={
                    "my-parameter": create_task.get_parameter("param-output"),
                    "binary-artifact": create_task.get_artifact("binary-output"),
                },
            )

            create_task >> consume_task
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: param-passing-
    spec:
      entrypoint: d
      serviceAccountName: argo
      templates:
      - name: d
        dag:
          tasks:
          - name: create-outputs
            template: create-outputs
          - name: consume-outputs
            depends: create-outputs
            template: consume-outputs
            arguments:
              artifacts:
              - name: binary-artifact
                from: '{{tasks.create-outputs.outputs.artifacts.binary-output}}'
              parameters:
              - name: my-parameter
                value: '{{tasks.create-outputs.outputs.parameters.param-output}}'
      - name: create-outputs
        outputs:
          artifacts:
          - name: binary-output
            path: /tmp/hera-outputs/artifacts/binary-output
            archive:
              none: {}
          parameters:
          - name: param-output
            valueFrom:
              path: /tmp/hera-outputs/parameters/param-output
        script:
          image: my-image:v1
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.scripts.custom_serialiser:create_outputs
          command:
          - python
          env:
          - name: hera__outputs_directory
            value: /tmp/hera-outputs
      - name: consume-outputs
        inputs:
          artifacts:
          - name: binary-artifact
            path: /tmp/hera-inputs/artifacts/binary-artifact
          parameters:
          - name: my-parameter
        script:
          image: my-image:v1
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.scripts.custom_serialiser:consume_outputs
          command:
          - python
    ```

