# New Resource Decorator



This example shows the use of the resource decorator and special Input/Output classes.


=== "Hera"

    ```python linenums="1"
    from typing_extensions import Annotated

    from hera.shared import global_config
    from hera.workflows import Input, Output, Parameter, Workflow

    global_config.experimental_features["decorator_syntax"] = True


    # We start by defining our Workflow
    w = Workflow(generate_name="resource-workflow-")


    # This defines the template's inputs
    class MyInput(Input):
        pvc_size: Annotated[
            int,
            Parameter(name="pvc-size"),
        ] = 10


    class MyOutput(Output):
        pvc_name: Annotated[
            str,
            Parameter(
                name="pvc-name",
                value_from={"jsonPath": "{.metadata.name}"},
            ),
        ]


    # We then use the decorators of the `Workflow` object
    # to set the entrypoint and create a Resouruce template
    @w.set_entrypoint
    @w.resource(
        action="create",
        set_owner_reference=True,
        manifest="""apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
        generateName: pvc-example-
    spec:
        accessModes: ['ReadWriteOnce', 'ReadOnlyMany']
        resources:
        requests:
            storage: '{{inputs.parameters.pvc-size}}'
    """,
    )
    def basic_hello_world(my_input: MyInput) -> MyOutput: ...
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: resource-workflow-
    spec:
      entrypoint: basic-hello-world
      templates:
      - name: basic-hello-world
        inputs:
          parameters:
          - name: pvc-size
            default: '10'
        outputs:
          parameters:
          - name: pvc-name
            valueFrom:
              jsonPath: '{.metadata.name}'
        resource:
          action: create
          manifest: |
            apiVersion: v1
            kind: PersistentVolumeClaim
            metadata:
                generateName: pvc-example-
            spec:
                accessModes: ['ReadWriteOnce', 'ReadOnlyMany']
                resources:
                requests:
                    storage: '{{inputs.parameters.pvc-size}}'
          setOwnerReference: true
    ```

