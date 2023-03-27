# Output Artifact S3

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/output-artifact-s3.yaml).



## Hera

```python
from hera.workflows import (
    Container,
    S3Artifact,
    Workflow,
    models as m,
)

with Workflow(generate_name="output-artifact-s3-", entrypoint="whalesay") as w:
    Container(
        name="whalesay",
        image="docker/whalesay:latest",
        command=["sh", "-c"],
        args=["cowsay hello world | tee /tmp/hello_world.txt"],
        outputs=[
            S3Artifact(
                name="message",
                path="/tmp",
                endpoint="s3.amazonaws.com",
                bucket="my-bucket",
                region="us-west-2",
                key="path/in/bucket/hello_world.txt.tgz",
                access_key_secret=m.SecretKeySelector(
                    name="my-s3-credentials",
                    key="accessKey",
                ),
                secret_key_secret=m.SecretKeySelector(
                    name="my-s3-credentials",
                    key="secretKey",
                ),
            )
        ],
    )
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: output-artifact-s3-
spec:
  entrypoint: whalesay
  templates:
  - container:
      args:
      - cowsay hello world | tee /tmp/hello_world.txt
      command:
      - sh
      - -c
      image: docker/whalesay:latest
    name: whalesay
    outputs:
      artifacts:
      - name: message
        path: /tmp
        s3:
          accessKeySecret:
            key: accessKey
            name: my-s3-credentials
          bucket: my-bucket
          endpoint: s3.amazonaws.com
          key: path/in/bucket/hello_world.txt.tgz
          region: us-west-2
          secretKeySecret:
            key: secretKey
            name: my-s3-credentials
```
