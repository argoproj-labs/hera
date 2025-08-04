# Env From






=== "Hera"

    ```python linenums="1"
    from hera.workflows import ConfigMapEnvFrom, Container, SecretEnvFrom, Workflow

    with Workflow(generate_name="secret-env-from-", entrypoint="whalesay") as w:
        whalesay = Container(
            name="whalesay",
            image="argoproj/argosay:v2",
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
      - name: whalesay
        container:
          image: argoproj/argosay:v2
          command:
          - cowsay
          envFrom:
          - prefix: abc
            secretRef:
              name: secret
              optional: false
          - prefix: abc
            configMapRef:
              name: configmap
              optional: false
    ```

