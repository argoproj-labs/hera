"""This example showcases how clients can mount secrets inside a task"""

from hera import Resources, SecretVolume, Task, Workflow, WorkflowService

# Create a secret with kubectl
# kubectl create secret generic secret-file --from-literal="config.json=SECRET_TOKEN"


def use_secret():
    with open("secret/config.json", "r") as secret_file:
        print(f"Secret: {secret_file.readline()}")


with Workflow("secret-volume", service=WorkflowService(host="my-argo-server.com", token="my-auth-token")) as w:
    Task(
        "use_secret",
        use_secret,
        resources=Resources(volumes=[SecretVolume(secret_name="secret-file", mount_path="/secret/")]),
    )

w.create()
