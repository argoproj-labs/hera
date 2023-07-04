# Resource Delete With Flags

> Note: This example is a replication of an Argo Workflow example in Hera. 




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Parameter,
        Resource,
        Step,
        Steps,
        Workflow,
        models as m,
    )

    with Workflow(
        generate_name="resource-delete-with-flags-",
        entrypoint="main",
    ) as w:
        create_configmap = Resource(
            name="create-configmap",
            action="create",
            manifest="""apiVersion: v1
    kind: ConfigMap
    metadata:
      name: resource-delete-with-flags
      labels:
        cleanup: "true"
    data:
      key: value
    """,
        )

        delete_resource = Resource(
            name="delete-resource",
            action="delete",
            flags=["configmap", "--selector", "{{inputs.parameters.selector}}"],
            inputs=m.Inputs(
                parameters=[Parameter(name="selector")],
            ),
        )

        with Steps(name="main") as s:
            Step(name="submit-resource", template=create_configmap.name)
            Step(
                name="delete-resource",
                template=delete_resource.name,
                arguments=[
                    Parameter(name="selector", value="cleanup=true"),
                ],
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: resource-delete-with-flags-
    spec:
      entrypoint: main
      templates:
      - name: create-configmap
        resource:
          action: create
          manifest: "apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: resource-delete-with-flags\n\
            \  labels:\n    cleanup: \"true\"\ndata:\n  key: value\n"
      - inputs:
          parameters:
          - name: selector
        name: delete-resource
        resource:
          action: delete
          flags:
          - configmap
          - --selector
          - '{{inputs.parameters.selector}}'
      - name: main
        steps:
        - - name: submit-resource
            template: create-configmap
        - - arguments:
              parameters:
              - name: selector
                value: cleanup=true
            name: delete-resource
            template: delete-resource
    ```

