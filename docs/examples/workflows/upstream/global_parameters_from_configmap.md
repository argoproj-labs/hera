# Global Parameters From Configmap

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/global-parameters-from-configmap.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Workflow
    from hera.workflows.models import Arguments, ConfigMapKeySelector, Parameter, ValueFrom

    with Workflow(
        arguments=Arguments(
            parameters=[
                Parameter(
                    name="message",
                    value_from=ValueFrom(
                        config_map_key_ref=ConfigMapKeySelector(
                            key="msg",
                            name="simple-parameters",
                        ),
                    ),
                )
            ],
        ),
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        annotations={
            "workflows.argoproj.io/description": 'This example demonstrates loading global parameter values from a ConfigMap.\nNote that the "simple-parameters" ConfigMap (defined in `examples/configmaps/simple-parameters-configmap.yaml`) needs to be created first before submitting this workflow.\n'
        },
        generate_name="global-parameter-values-from-configmap-",
        labels={"workflows.argoproj.io/test": "true"},
        entrypoint="print-message",
    ) as w:
        Container(
            name="print-message",
            args=["{{workflow.parameters.message}}"],
            command=["echo"],
            image="busybox",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: global-parameter-values-from-configmap-
      annotations:
        workflows.argoproj.io/description: |
          This example demonstrates loading global parameter values from a ConfigMap.
          Note that the "simple-parameters" ConfigMap (defined in `examples/configmaps/simple-parameters-configmap.yaml`) needs to be created first before submitting this workflow.
      labels:
        workflows.argoproj.io/test: 'true'
    spec:
      entrypoint: print-message
      templates:
      - name: print-message
        container:
          image: busybox
          args:
          - '{{workflow.parameters.message}}'
          command:
          - echo
      arguments:
        parameters:
        - name: message
          valueFrom:
            configMapKeyRef:
              name: simple-parameters
              key: msg
    ```

