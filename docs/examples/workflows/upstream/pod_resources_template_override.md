# Pod Resources Template Override

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/pod-resources-template-override.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Resources, Step, Steps, UserContainer, Workflow

    with Workflow(
        generate_name="pod-resources-template-override-",
        entrypoint="main",
        pod_resources=Resources(cpu_limit="1", memory_limit="512Mi"),
    ) as w:
        small = Container(
            name="small",
            image="busybox",
            command=["echo"],
            args=["small step"],
        )
        large = Container(
            name="large",
            pod_resources=Resources(cpu_limit="2", memory_limit="1Gi"),
            image="busybox",
            command=["sh", "-c"],
            args=["sleep 5; echo large step"],
            sidecars=UserContainer(name="helper", image="busybox", command=["sh", "-c"], args=["sleep 10"]),
        )

        with Steps(name="main") as s:
            Step(name="small", template=small)
            Step(name="large", template=large)
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: pod-resources-template-override-
    spec:
      entrypoint: main
      templates:
      - name: small
        container:
          image: busybox
          args:
          - small step
          command:
          - echo
      - name: large
        sidecars:
        - name: helper
          image: busybox
          args:
          - sleep 10
          command:
          - sh
          - -c
        container:
          image: busybox
          args:
          - sleep 5; echo large step
          command:
          - sh
          - -c
        podResources:
          limits:
            cpu: '2'
            memory: 1Gi
      - name: main
        steps:
        - - name: small
            template: small
        - - name: large
            template: large
      podResources:
        limits:
          cpu: '1'
          memory: 512Mi
    ```

