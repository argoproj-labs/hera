"""This example showcases how to use WebHDFS.

This example used to reside in the `examples` directory, but was moved here to avoid the extra `overwrite` parameter
specified in the `outputs` field upstream, which is not an allowed parameter. Example:
- https://github.com/argoproj/argo-workflows/blob/master/examples/webhdfs-input-output-artifacts.yaml
"""
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
