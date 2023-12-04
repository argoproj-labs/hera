# Image Pull Secrets

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/image-pull-secrets.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Workflow

    with Workflow(generate_name="hello-world-", image_pull_secrets="docker-registry-secret", entrypoint="whalesay") as w:
        Container(name="whalesay", image="docker/whalesay:latest", command=["cowsay"], args=["hello world"])
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: hello-world-
    spec:
      entrypoint: whalesay
      imagePullSecrets:
      - name: docker-registry-secret
      templates:
      - container:
          args:
          - hello world
          command:
          - cowsay
          image: docker/whalesay:latest
        name: whalesay
    ```

