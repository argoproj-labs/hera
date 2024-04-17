# Env From






=== "Hera"

    ```python linenums="1"
    from hera.workflows import ConfigMapEnvFrom, Container, SecretEnvFrom, Workflow

    with Workflow(generate_name="secret-env-from-", entrypoint="whalesay") as w:
        whalesay = Container(
            image="docker/whalesay:latest",
            command=["cowsay"],
            env_from=[
                SecretEnvFrom(prefix="abc", name="secret", optional=False),
                ConfigMapEnvFrom(prefix="abc", name="configmap", optional=False),
            ],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: secret-env-from-
    spec:
      entrypoint: whalesay
      templates:
      - container:
          command:
          - cowsay
          envFrom:
          - prefix: abc
            secretRef:
              name: secret
              optional: false
          - configMapRef:
              name: configmap
              optional: false
            prefix: abc
          image: docker/whalesay:latest
    ```

