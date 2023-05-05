# Sidecar Dind



This example showcases how one can run Docker in Docker with a sidecar container with Hera


=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Env, UserContainer, Workflow
    from hera.workflows.models import SecurityContext

    # this assumes you have set a global token and a global host
    with Workflow(generate_name="sidecar-dind-", entrypoint="sidecar-dind-example") as w:
        Container(
            name="sidecar-dind-example",
            image="docker:19.03.13",
            command=["sh", "-c"],
            args=["until docker ps; do sleep 3; done; docker run --rm debian:latest cat /etc/os-release"],
            env=[Env(name="DOCKER_HOST", value="127.0.0.1")],
            sidecars=UserContainer(
                name="dind",
                image="docker:19.03.13-dind",
                command=["dockerd-entrypoint.sh"],
                env=[Env(name="DOCKER_TLS_CERTDIR", value="")],
                security_context=SecurityContext(privileged=True),
                mirror_volume_mounts=True,
            ),
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: sidecar-dind-
    spec:
      entrypoint: sidecar-dind-example
      templates:
      - container:
          args:
          - until docker ps; do sleep 3; done; docker run --rm debian:latest cat /etc/os-release
          command:
          - sh
          - -c
          env:
          - name: DOCKER_HOST
            value: 127.0.0.1
          image: docker:19.03.13
        name: sidecar-dind-example
        sidecars:
        - command:
          - dockerd-entrypoint.sh
          env:
          - name: DOCKER_TLS_CERTDIR
            value: ''
          image: docker:19.03.13-dind
          mirrorVolumeMounts: true
          name: dind
          securityContext:
            privileged: true
    ```

