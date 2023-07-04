# Daemon Nginx

> Note: This example is a replication of an Argo Workflow example in Hera. 




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Container,
        Parameter,
        Steps,
        Workflow,
        models as m,
    )

    with Workflow(
        generate_name="daemon-nginx-",
        entrypoint="daemon-nginx-example",
    ) as w:
        nginx_server = Container(
            name="nginx-server",
            daemon=True,
            image="nginx:1.13",
            readiness_probe=m.Probe(
                http_get=m.HTTPGetAction(
                    path="/",
                    port=80,
                ),
                initial_delay_seconds=2,
                timeout_seconds=1,
            ),
        )
        nginx_client = Container(
            name="nginx-client",
            inputs=Parameter(name="server-ip"),
            image="appropriate/curl:latest",
            command=["/bin/sh", "-c"],
            args=[
                "echo curl --silent -G http://{{inputs.parameters.server-ip}}:80/ && curl "
                "--silent -G http://{{inputs.parameters.server-ip}}:80/"
            ],
        )
        with Steps(name="daemon-nginx-example"):
            s = nginx_server()
            nginx_client(arguments={"server-ip": s.ip})
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: daemon-nginx-
    spec:
      entrypoint: daemon-nginx-example
      templates:
      - container:
          image: nginx:1.13
          readinessProbe:
            httpGet:
              path: /
              port: '80'
            initialDelaySeconds: 2
            timeoutSeconds: 1
        daemon: true
        name: nginx-server
      - container:
          args:
          - echo curl --silent -G http://{{inputs.parameters.server-ip}}:80/ && curl --silent
            -G http://{{inputs.parameters.server-ip}}:80/
          command:
          - /bin/sh
          - -c
          image: appropriate/curl:latest
        inputs:
          parameters:
          - name: server-ip
        name: nginx-client
      - name: daemon-nginx-example
        steps:
        - - name: nginx-server
            template: nginx-server
        - - arguments:
              parameters:
              - name: server-ip
                value: '{{steps.nginx-server.ip}}'
            name: nginx-client
            template: nginx-client
    ```

