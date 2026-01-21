# Dns Config

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/dns-config.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Workflow
    from hera.workflows.models import PodDNSConfig, PodDNSConfigOption, Quantity, ResourceRequirements

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="test-dns-config-",
        dns_config=PodDNSConfig(
            nameservers=["1.2.3.4"],
            options=[
                PodDNSConfigOption(
                    name="ndots",
                    value="2",
                )
            ],
        ),
        entrypoint="hello-world",
    ) as w:
        Container(
            name="hello-world",
            args=["hello world"],
            command=["echo"],
            image="busybox",
            resources=ResourceRequirements(
                limits={
                    "memory": Quantity(
                        root="32Mi",
                    ),
                    "cpu": Quantity(
                        root="100m",
                    ),
                },
            ),
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: test-dns-config-
    spec:
      entrypoint: hello-world
      templates:
      - name: hello-world
        container:
          image: busybox
          args:
          - hello world
          command:
          - echo
          resources:
            limits:
              cpu: 100m
              memory: 32Mi
      dnsConfig:
        nameservers:
        - 1.2.3.4
        options:
        - name: ndots
          value: '2'
    ```

