# Sidecar Nginx

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/sidecar-nginx.yaml).

This example showcases how one can run an Nginx sidecar container with Hera


=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, UserContainer, Workflow

    with Workflow(generate_name="sidecar-nginx-", entrypoint="sidecar-nginx-example") as w:
        Container(
            name="sidecar-nginx-example",
            image="appropriate/curl",
            command=["sh", "-c"],
            args=["until `curl -G 'http://127.0.0.1/' >& /tmp/out`; do echo sleep && sleep 1; done && cat /tmp/out"],
            sidecars=UserContainer(name="nginx", image="nginx:1.13", command=["nginx", "-g", "daemon off;"]),
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: sidecar-nginx-
    spec:
      entrypoint: sidecar-nginx-example
      templates:
      - name: sidecar-nginx-example
        sidecars:
        - name: nginx
          image: nginx:1.13
          command:
          - nginx
          - -g
          - daemon off;
        container:
          image: appropriate/curl
          args:
          - until `curl -G 'http://127.0.0.1/' >& /tmp/out`; do echo sleep && sleep 1;
            done && cat /tmp/out
          command:
          - sh
          - -c
    ```

