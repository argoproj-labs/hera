"""This example showcases how clients can mount secrets inside a task"""
from hera.resources import Resources
from hera.task import Task
from hera.volumes import SecretVolume
from hera.workflow import Workflow
from hera.workflow_service import WorkflowService

# Create a secret with kubectl
# kubectl create secret generic secret-file --from-literal="config.json=SECRET_TOKEN"


def use_secret():
    with open("secret/config.json", "r") as secret_file:
        print(f"Secret: {secret_file.readline()}")


# TODO: replace the domain and token with your own
ws = WorkflowService(host='my-argo-server.com', token='my-auth-token')
w = Workflow('volume-provision', ws)
d = Task(
    'use_secret',
    use_secret,
    resources=Resources(secret_volume=SecretVolume(secret_name='secret-file', mount_path='/secret/')),
)

w.add_task(d)
w.submit()
