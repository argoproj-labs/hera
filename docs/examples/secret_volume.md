# Secret volume

This example showcases how clients can mount secrets inside a task

```python
from hera import SecretVolume, Task, Workflow

# Create a secret with kubectl
# kubectl create secret generic secret-file --from-literal="config.json=SECRET_TOKEN"
# (Remember to add --namespace <namespace> if not default)


def use_secret():
    with open("secret/config.json", "r") as secret_file:
        print(f"Secret: {secret_file.readline()}")


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow("secret-volume") as w:
    Task("use_secret", use_secret, volumes=[SecretVolume(secret_name="secret-file", mount_path="/secret/")])

w.create()

```