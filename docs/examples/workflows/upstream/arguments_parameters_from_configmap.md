# Arguments Parameters From Configmap

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/arguments-parameters-from-configmap.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Container,
        Parameter,
        Workflow,
        models as m,
    )

    with Workflow(
        generate_name="arguments-parameters-from-configmap-",
        entrypoint="whalesay",
        service_account_name="argo",
    ) as w:
        Container(
            name="whalesay",
            image="argoproj/argosay:v2",
            args=["echo", "{{inputs.parameters.message}}"],
            inputs=Parameter(
                name="message",
                value_from=m.ValueFrom(
                    config_map_key_ref=m.ConfigMapKeySelector(
                        name="simple-parameters",
                        key="msg",
                    )
                ),
            ),
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: arguments-parameters-from-configmap-
    spec:
      entrypoint: whalesay
      serviceAccountName: argo
      templates:
      - container:
          args:
          - echo
          - '{{inputs.parameters.message}}'
          image: argoproj/argosay:v2
        inputs:
          parameters:
          - name: message
            valueFrom:
              configMapKeyRef:
                key: msg
                name: simple-parameters
        name: whalesay
    ```

