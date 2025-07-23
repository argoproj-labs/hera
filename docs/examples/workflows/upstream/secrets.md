# Secrets

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/secrets.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Workflow
    from hera.workflows.models import EnvVar, EnvVarSource, SecretKeySelector, SecretVolumeSource, Volume, VolumeMount

    with Workflow(
        volumes=[
            Volume(
                name="my-secret-vol",
                secret=SecretVolumeSource(
                    secret_name="my-secret",
                ),
            )
        ],
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="secrets-",
        entrypoint="print-secret",
    ) as w:
        Container(
            name="print-secret",
            args=[
                ' echo "secret from env: $MYSECRETPASSWORD"; echo "secret from file: `cat /secret/mountpath/mypassword`" '
            ],
            command=["sh", "-c"],
            env=[
                EnvVar(
                    name="MYSECRETPASSWORD",
                    value_from=EnvVarSource(
                        secret_key_ref=SecretKeySelector(
                            key="mypassword",
                            name="my-secret",
                        ),
                    ),
                )
            ],
            image="alpine:3.7",
            volume_mounts=[
                VolumeMount(
                    mount_path="/secret/mountpath",
                    name="my-secret-vol",
                )
            ],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: secrets-
    spec:
      entrypoint: print-secret
      templates:
      - name: print-secret
        container:
          image: alpine:3.7
          args:
          - ' echo "secret from env: $MYSECRETPASSWORD"; echo "secret from file: `cat
            /secret/mountpath/mypassword`" '
          command:
          - sh
          - -c
          env:
          - name: MYSECRETPASSWORD
            valueFrom:
              secretKeyRef:
                name: my-secret
                key: mypassword
          volumeMounts:
          - name: my-secret-vol
            mountPath: /secret/mountpath
      volumes:
      - name: my-secret-vol
        secret:
          secretName: my-secret
    ```

