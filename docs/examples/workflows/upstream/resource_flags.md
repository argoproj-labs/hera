# Resource Flags

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/resource-flags.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Resource, Step, Steps, Workflow
    from hera.workflows.models import ContinueOn

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="resource-validate-",
        entrypoint="resource-validate-example",
    ) as w:
        with Steps(
            name="resource-validate-example",
        ) as invocator:
            Step(
                name="submit-resource",
                continue_on=ContinueOn(
                    failed=True,
                ),
                template="create-route",
            )
            Step(
                name="submit-resource-without-validation",
                template="create-route-without-validation",
                when="{{steps.submit-resource.status}} == Failed",
            )
        Resource(
            name="create-route",
            action="create",
            manifest="apiVersion: route.openshift.io/v1\nkind: Route\nmetadata:\n  name: host-route\nspec:\n  to:\n    kind: Service\n    name: service-name\n",
        )
        Resource(
            name="create-route-without-validation",
            action="create",
            flags=["--validate=false"],
            manifest="apiVersion: route.openshift.io/v1\nkind: Route\nmetadata:\n  name: host-route\nspec:\n  to:\n    kind: Service\n    name: service-name\n",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: resource-validate-
    spec:
      entrypoint: resource-validate-example
      templates:
      - name: resource-validate-example
        steps:
        - - name: submit-resource
            template: create-route
            continueOn:
              failed: true
        - - name: submit-resource-without-validation
            template: create-route-without-validation
            when: '{{steps.submit-resource.status}} == Failed'
      - name: create-route
        resource:
          action: create
          manifest: |
            apiVersion: route.openshift.io/v1
            kind: Route
            metadata:
              name: host-route
            spec:
              to:
                kind: Service
                name: service-name
      - name: create-route-without-validation
        resource:
          action: create
          manifest: |
            apiVersion: route.openshift.io/v1
            kind: Route
            metadata:
              name: host-route
            spec:
              to:
                kind: Service
                name: service-name
          flags:
          - --validate=false
    ```

