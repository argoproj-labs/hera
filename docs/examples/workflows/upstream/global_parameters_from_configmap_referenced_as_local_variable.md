# Global Parameters From Configmap Referenced As Local Variable

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/global-parameters-from-configmap-referenced-as-local-variable.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Container,
        Parameter,
        Workflow,
        models as m,
    )

    with Workflow(
        generate_name="global-parameter-from-configmap-referenced-as-local-variable-",
        entrypoint="print-message",
        arguments=Parameter(
            name="message",
            value_from=m.ValueFrom(config_map_key_ref=m.ConfigMapKeySelector(name="simple-parameters", key="msg")),
        ),
    ) as w:
        Container(
            name="print-message",
            image="busybox",
            command=["echo"],
            args=["{{inputs.parameters.message}}"],
            inputs=Parameter(name="message"),
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: global-parameter-from-configmap-referenced-as-local-variable-
    spec:
      entrypoint: print-message
      templates:
      - name: print-message
        container:
          image: busybox
          args:
          - '{{inputs.parameters.message}}'
          command:
          - echo
        inputs:
          parameters:
          - name: message
      arguments:
        parameters:
        - name: message
          valueFrom:
            configMapKeyRef:
              name: simple-parameters
              key: msg
    ```

