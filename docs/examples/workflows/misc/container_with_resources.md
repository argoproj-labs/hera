# Container With Resources






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Resources, Workflow

    with Workflow(generate_name="container-with-resources-", entrypoint="c") as w:
        Container(
            name="c",
            image="alpine:3.7",
            command=["sh", "-c"],
            args=["echo Hello, world!"],
            resources=Resources(cpu_request=1, memory_request="5Gi", ephemeral_request="5Gi"),
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: container-with-resources-
    spec:
      entrypoint: c
      templates:
      - name: c
        container:
          image: alpine:3.7
          args:
          - echo Hello, world!
          command:
          - sh
          - -c
          resources:
            requests:
              cpu: '1'
              ephemeral-storage: 5Gi
              memory: 5Gi
    ```

