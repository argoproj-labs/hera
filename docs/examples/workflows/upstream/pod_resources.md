# Pod Resources

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/pod-resources.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Resources, Workflow

    with Workflow(
        generate_name="pod-resources-",
        entrypoint="hello-world",
        pod_resources=Resources(
            cpu_request="100m",
            memory_request="64Mi",
            cpu_limit="1",
            memory_limit="512Mi",
        ),
    ) as w:
        Container(
            name="hello-world",
            image="busybox",
            command=["echo"],
            args=["hello world"],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: pod-resources-
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
      podResources:
        limits:
          cpu: '1'
          memory: 512Mi
        requests:
          cpu: 100m
          memory: 64Mi
    ```

