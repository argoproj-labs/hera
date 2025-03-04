# Webhdfs Input Output Artifacts

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/webhdfs-input-output-artifacts.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Container,
        HTTPArtifact,
        Workflow,
        models as m,
    )

    with Workflow(
        generate_name="input-output-artifact-webhdfs-",
        entrypoint="input-output-artifact-webhdfs-example",
    ) as w:
        Container(
            name="input-output-artifact-webhdfs-example",
            image="debian:latest",
            command=["sh", "-c"],
            args=["cat /my-artifact"],
            inputs=[
                HTTPArtifact(
                    name="my-art",
                    path="/my-artifact",
                    url="https://mywebhdfsprovider.com/webhdfs/v1/file.txt?op=OPEN",
                    auth=m.HTTPAuth(
                        oauth2=m.OAuth2Auth(
                            client_id_secret=m.SecretKeySelector(name="oauth-sec", key="clientID"),
                            client_secret_secret=m.SecretKeySelector(name="oauth-sec", key="clientSecret"),
                            token_url_secret=m.SecretKeySelector(
                                name="oauth-sec",
                                key="tokenURL",
                            ),
                            scopes=["some", "scopes"],
                            endpoint_params=[
                                m.OAuth2EndpointParam(key="customkey", value="customvalue"),
                            ],
                        ),
                    ),
                    headers=[
                        m.Header(name="CustomHeader", value="CustomValue"),
                    ],
                )
            ],
            outputs=[
                HTTPArtifact(
                    name="my-art2",
                    path="/my-artifact",
                    url="https://mywebhdfsprovider.com/webhdfs/v1/file.txt?op=CREATE&overwrite=true",
                    auth=m.HTTPAuth(
                        client_cert=m.ClientCertAuth(
                            client_cert_secret=m.SecretKeySelector(
                                name="cert-sec",
                                key="certificate.pem",
                            ),
                            client_key_secret=m.SecretKeySelector(
                                name="cert-sec",
                                key="key.pem",
                            ),
                        )
                    ),
                    headers=[m.Header(name="CustomHeader", value="CustomValue")],
                )
            ],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: input-output-artifact-webhdfs-
    spec:
      entrypoint: input-output-artifact-webhdfs-example
      templates:
      - name: input-output-artifact-webhdfs-example
        container:
          image: debian:latest
          args:
          - cat /my-artifact
          command:
          - sh
          - -c
        inputs:
          artifacts:
          - name: my-art
            path: /my-artifact
            http:
              url: https://mywebhdfsprovider.com/webhdfs/v1/file.txt?op=OPEN
              headers:
              - name: CustomHeader
                value: CustomValue
              auth:
                oauth2:
                  endpointParams:
                  - key: customkey
                    value: customvalue
                  scopes:
                  - some
                  - scopes
                  clientIDSecret:
                    name: oauth-sec
                    key: clientID
                  clientSecretSecret:
                    name: oauth-sec
                    key: clientSecret
                  tokenURLSecret:
                    name: oauth-sec
                    key: tokenURL
        outputs:
          artifacts:
          - name: my-art2
            path: /my-artifact
            http:
              url: https://mywebhdfsprovider.com/webhdfs/v1/file.txt?op=CREATE&overwrite=true
              headers:
              - name: CustomHeader
                value: CustomValue
              auth:
                clientCert:
                  clientCertSecret:
                    name: cert-sec
                    key: certificate.pem
                  clientKeySecret:
                    name: cert-sec
                    key: key.pem
    ```

