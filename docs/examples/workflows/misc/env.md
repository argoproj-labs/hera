# Env






=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        ConfigMapEnv,
        ConfigMapEnvFrom,
        Container,
        Env,
        ResourceEnv,
        SecretEnv,
        SecretEnvFrom,
        Workflow,
    )

    with Workflow(generate_name="secret-env-from-", entrypoint="whalesay") as w:
        whalesay = Container(
            name="whalesay",
            image="docker/whalesay:latest",
            command=["cowsay"],
            env_from=[
                SecretEnvFrom(prefix="abc", name="secret", optional=False),
                ConfigMapEnvFrom(prefix="abc", name="configmap", optional=False),
            ],
            env=[
                Env(name="test", value="1"),
                SecretEnv(name="s1", secret_key="s1", secret_name="abc"),
                ResourceEnv(name="r1", resource="abc"),
                ConfigMapEnv(name="c1", config_map_key="c1", config_map_name="abc"),
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
          image: docker/whalesay:latest
          command:
          - cowsay
          env:
          - name: test
            value: '1'
          - name: s1
            valueFrom:
              secretKeyRef:
                name: abc
                key: s1
          - name: r1
            valueFrom:
              resourceFieldRef:
                resource: abc
          - name: c1
            valueFrom:
              configMapKeyRef:
                name: abc
                key: c1
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

