# Default Pdb Support

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/default-pdb-support.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Container,
        Workflow,
        models as m,
    )

    with Workflow(
        generate_name="default-pdb-support-",
        entrypoint="pdbcreate",
        service_account_name="default",
        pod_disruption_budget=m.PodDisruptionBudgetSpec(min_available=9999),
    ) as w:
        Container(
            name="pdbcreate",
            image="alpine:latest",
            command=["sh", "-c"],
            args=["sleep 10"],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: default-pdb-support-
    spec:
      entrypoint: pdbcreate
      podDisruptionBudget:
        minAvailable: '9999'
      serviceAccountName: default
      templates:
      - container:
          args:
          - sleep 10
          command:
          - sh
          - -c
          image: alpine:latest
        name: pdbcreate
    ```

