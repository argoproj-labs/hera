# Init Containers With Env



This example showcases how to run a init_containers with env


=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Env, SecretEnv, UserContainer, Workflow

    with Workflow(generate_name="container-", entrypoint="cowsay") as w:
        Container(
            name="cowsay",
            image="docker/whalesay",
            command=["cowsay", "foo"],
            init_containers=[
                UserContainer(
                    name="init",
                    image="busybox",
                    command=[
                        "sh",
                        "-c",
                        "echo Hello from the init container ($FOO, $SECRET)",
                    ],
                    env=[
                        Env(name="FOO", value="bar"),
                        SecretEnv(name="SECRET", secret_key="password", secret_name="my-secret"),
                    ],
                )
            ],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: container-
    spec:
      entrypoint: cowsay
      templates:
      - container:
          command:
          - cowsay
          - foo
          image: docker/whalesay
        initContainers:
        - command:
          - sh
          - -c
          - echo Hello from the init container ($FOO, $SECRET)
          env:
          - name: FOO
            value: bar
          - name: SECRET
            valueFrom:
              secretKeyRef:
                key: password
                name: my-secret
          image: busybox
          name: init
        name: cowsay
    ```

